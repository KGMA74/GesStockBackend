#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GesStockBackend.settings')
django.setup()

from api.models import User, Store, Warehouse, Product, ProductStock, StockTransfer, StockTransferItem
from decimal import Decimal

def test_stock_transfer():
    print("🧪 Test des transferts de stock avec le nouveau modèle StockTransfer")
    
    # Récupérer les données existantes
    store = Store.objects.first()
    user = User.objects.first()
    
    # Créer deux entrepôts si ils n'existent pas
    warehouse_1, created = Warehouse.objects.get_or_create(
        name="Entrepôt Principal",
        defaults={'store': store, 'address': 'Adresse 1'}
    )
    print(f"✅ Entrepôt source: {warehouse_1.name}")
    
    warehouse_2, created = Warehouse.objects.get_or_create(
        name="Entrepôt Secondaire", 
        defaults={'store': store, 'address': 'Adresse 2'}
    )
    print(f"✅ Entrepôt destination: {warehouse_2.name}")
    
    # Créer un produit si il n'existe pas
    product, created = Product.objects.get_or_create(
        reference="PROD-TRANSFER-002",
        defaults={
            'name': "Produit Test Transfert V2",
            'unit': "pièce",
            'store': store,
            'sale_price': Decimal('750.00')
        }
    )
    print(f"✅ Produit: {product.reference}")
    
    # S'assurer qu'il y a du stock dans l'entrepôt source
    stock_source, created = ProductStock.objects.get_or_create(
        product=product,
        warehouse=warehouse_1,
        defaults={'quantity': 0}
    )
    
    if stock_source.quantity < 15:
        stock_source.quantity = 25  # Ajouter du stock pour le test
        stock_source.save()
    
    print(f"✅ Stock initial dans {warehouse_1.name}: {stock_source.quantity}")
    
    # Vérifier le stock initial dans l'entrepôt de destination
    stock_dest, created = ProductStock.objects.get_or_create(
        product=product,
        warehouse=warehouse_2,
        defaults={'quantity': 0}
    )
    initial_dest_stock = stock_dest.quantity
    print(f"✅ Stock initial dans {warehouse_2.name}: {initial_dest_stock}")
    
    # Créer un transfert
    print("\n🔄 Création du transfert...")
    transfer = StockTransfer.objects.create(
        from_warehouse=warehouse_1,
        to_warehouse=warehouse_2,
        notes="Test du nouveau modèle StockTransfer",
        created_by=user
    )
    print(f"✅ Transfert créé: {transfer.transfer_number} (Statut: {transfer.get_status_display()})")
    
    # Ajouter des articles au transfert
    transfer_item = StockTransferItem.objects.create(
        stock_transfer=transfer,
        product=product,
        quantity=8
    )
    print(f"✅ Article ajouté: {product.reference} x{transfer_item.quantity}")
    
    # Vérifier les stocks avant transfert (ne devraient pas avoir changé)
    stock_source.refresh_from_db()
    stock_dest.refresh_from_db()
    
    print(f"\n📊 État AVANT exécution du transfert:")
    print(f"   Stock source ({warehouse_1.name}): {stock_source.quantity}")
    print(f"   Stock destination ({warehouse_2.name}): {stock_dest.quantity}")
    print(f"   Statut transfert: {transfer.get_status_display()}")
    
    # Exécuter le transfert
    print(f"\n🎯 Exécution du transfert...")
    transfer.complete_transfer()
    
    # Vérifier les stocks après transfert
    stock_source.refresh_from_db()
    stock_dest.refresh_from_db()
    transfer.refresh_from_db()
    
    print(f"\n📊 État APRÈS exécution du transfert:")
    print(f"   Stock source ({warehouse_1.name}): {stock_source.quantity}")
    print(f"   Stock destination ({warehouse_2.name}): {stock_dest.quantity}")
    print(f"   Différence source: -{transfer_item.quantity}")
    print(f"   Différence destination: +{transfer_item.quantity}")
    print(f"   Statut transfert: {transfer.get_status_display()}")
    print(f"   Terminé le: {transfer.completed_at}")
    
    # Vérifier les calculs
    expected_source = 25 - transfer_item.quantity
    expected_dest = initial_dest_stock + transfer_item.quantity
    
    if stock_source.quantity == expected_source and stock_dest.quantity == expected_dest:
        print(f"\n🎉 Test réussi ! Les stocks ont été correctement transférés")
    else:
        print(f"\n❌ Erreur dans les calculs:")
        print(f"   Source attendu: {expected_source}, réel: {stock_source.quantity}")
        print(f"   Destination attendu: {expected_dest}, réel: {stock_dest.quantity}")
    
    print(f"\n🏁 Test terminé!")
    print(f"   Transfer Number: {transfer.transfer_number}")
    print(f"   Statut final: {transfer.get_status_display()}")
    print(f"   Nombre d'articles: {transfer.items.count()}")

if __name__ == '__main__':
    test_stock_transfer()
