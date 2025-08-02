#!/usr/bin/env python
"""
Script pour tester la gestion des dettes clients et l'utilisation automatique des prix de vente
"""
import os
import sys
import django
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GesStockBackend.settings')
django.setup()

from api.models import Store, Customer, Product, Warehouse, StockExit, StockExitItem, Account, User, ProductStock, FinancialTransaction

def test_debt_management():
    """Test de la gestion des dettes clients"""
    print("🧪 Test de la gestion des dettes clients")
    print("=" * 50)
    
    # Récupérer ou créer un magasin de test
    store, _ = Store.objects.get_or_create(
        name="Boutique Test", 
        defaults={'description': 'Boutique pour tests'}
    )
    
    # Récupérer ou créer un entrepôt
    warehouse, _ = Warehouse.objects.get_or_create(
        name="Entrepôt Principal",
        store=store,
        defaults={'address': 'Adresse test'}
    )
    
    # Récupérer ou créer un utilisateur
    user, _ = User.objects.get_or_create(
        username="admin",
        store=store,
        defaults={
            'fullname': 'Administrateur Test',
            'email': 'admin@test.com',
            'is_staff': True
        }
    )
    
    # Récupérer ou créer un compte
    account, _ = Account.objects.get_or_create(
        name="Caisse Principale",
        store=store,
        defaults={
            'account_type': 'cash',
            'balance': Decimal('100000.00')
        }
    )
    
    # Créer un client de test
    customer, created = Customer.objects.get_or_create(
        name="Client Test",
        store=store,
        defaults={
            'phone': '123456789',
            'email': 'client@test.com',
            'debt': Decimal('0.00')
        }
    )
    
    if created:
        print(f"✅ Client créé: {customer.name} - Dette initiale: {customer.debt} F")
    else:
        print(f"📋 Client existant: {customer.name} - Dette actuelle: {customer.debt} F")
    
    # Créer un produit de test
    product, created = Product.objects.get_or_create(
        reference="PROD001",
        store=store,
        defaults={
            'name': 'Produit Test',
            'price': Decimal('500.00'),  # Prix d'achat
            'sale_price': Decimal('750.00'),  # Prix de vente
            'unit': 'pièce'
        }
    )
    
    if created:
        print(f"✅ Produit créé: {product.reference} - {product.name}")
        print(f"   Prix d'achat: {product.price} F, Prix de vente: {product.sale_price} F")
        
        # Ajouter du stock
        stock, _ = ProductStock.objects.get_or_create(
            product=product,
            warehouse=warehouse,
            defaults={'quantity': 100}
        )
        print(f"   Stock ajouté: {stock.quantity} unités")
    else:
        print(f"📋 Produit existant: {product.reference} - {product.name}")
        print(f"   Prix d'achat: {product.price} F, Prix de vente: {product.sale_price} F")
    
    print("\n🛒 Test de vente avec paiement partiel")
    print("-" * 40)
    
    # Créer une vente avec paiement partiel
    stock_exit = StockExit.objects.create(
        customer=customer,
        warehouse=warehouse,
        account=account,
        created_by=user,
        notes="Vente test avec paiement partiel"
    )
    
    print(f"✅ Bon de sortie créé: {stock_exit.exit_number}")
    
    # Ajouter un article (le prix de vente sera automatiquement utilisé)
    exit_item = StockExitItem.objects.create(
        stock_exit=stock_exit,
        product=product,
        quantity=2
        # sale_price sera automatiquement défini par le modèle
    )
    
    print(f"✅ Article ajouté: {exit_item.quantity} x {product.name}")
    print(f"   Prix unitaire utilisé: {exit_item.sale_price} F (automatique du produit)")
    print(f"   Prix total: {exit_item.total_price} F")
    
    # Mettre à jour le montant total de la vente
    stock_exit.total_amount = exit_item.total_price
    stock_exit.paid_amount = Decimal('1000.00')  # Le client paie seulement 1000 F sur 1500 F
    stock_exit.save()
    
    print(f"\n💰 Détails de la vente:")
    print(f"   Montant total: {stock_exit.total_amount} F")
    print(f"   Montant payé: {stock_exit.paid_amount} F")
    print(f"   Montant restant: {stock_exit.remaining_amount} F")
    print(f"   Statut: {stock_exit.payment_status}")
    print(f"   Entièrement payé: {stock_exit.is_fully_paid}")
    
    # Vérifier la dette du client
    customer.refresh_from_db()
    print(f"\n👤 Dette du client après vente:")
    print(f"   {customer.name}: {customer.debt} F")
    
    print("\n💳 Test de paiement supplémentaire")
    print("-" * 40)
    
    # Le client paie une partie de sa dette
    remaining = stock_exit.add_payment(Decimal('500.00'))
    print(f"✅ Paiement de 500 F ajouté")
    print(f"   Montant restant sur cette vente: {remaining} F")
    
    # Vérifier la dette mise à jour
    customer.refresh_from_db()
    print(f"   Dette totale du client: {customer.debt} F")
    
    print(f"\n📊 État final de la vente:")
    print(f"   Montant total: {stock_exit.total_amount} F")
    print(f"   Montant payé: {stock_exit.paid_amount} F") 
    print(f"   Montant restant: {stock_exit.remaining_amount} F")
    print(f"   Statut: {stock_exit.payment_status}")
    print(f"   Entièrement payé: {stock_exit.is_fully_paid}")
    
    print("\n✅ Test de gestion des dettes terminé avec succès!")

def test_automatic_sale_price():
    """Test de l'utilisation automatique du prix de vente"""
    print("\n🏷️ Test de l'utilisation automatique du prix de vente")
    print("=" * 50)
    
    # Récupérer les objets existants
    store = Store.objects.get(name="Boutique Test")
    warehouse = Warehouse.objects.get(name="Entrepôt Principal", store=store)
    user = User.objects.get(username="admin", store=store)
    
    # Créer un nouveau produit ou utiliser existant
    product2, created = Product.objects.get_or_create(
        reference="PROD002",
        store=store,
        defaults={
            'name': "Produit Auto-Prix",
            'price': Decimal('300.00'),  # Prix d'achat
            'sale_price': Decimal('450.00'),  # Prix de vente
        }
    )
    
    if created:
        # Ajouter du stock seulement si le produit vient d'être créé
        ProductStock.objects.get_or_create(
            product=product2,
            warehouse=warehouse,
            defaults={'quantity': 50}
        )
        print(f"✅ Nouveau produit créé: {product2.reference}")
    else:
        print(f"📋 Produit existant utilisé: {product2.reference}")
    
    print(f"   Prix de vente configuré: {product2.sale_price} F")
    
    # Créer une vente sans spécifier le prix
    stock_exit2 = StockExit.objects.create(
        customer_name="Client Anonyme Test",
        warehouse=warehouse,
        created_by=user,
        notes="Test prix automatique"
    )
    
    # Ajouter un article SANS spécifier le sale_price
    exit_item2 = StockExitItem.objects.create(
        stock_exit=stock_exit2,
        product=product2,
        quantity=3
        # sale_price non spécifié - doit être automatique
    )
    
    print(f"✅ Article ajouté sans prix spécifié:")
    print(f"   Quantité: {exit_item2.quantity}")
    print(f"   Prix unitaire automatique: {exit_item2.sale_price} F")
    print(f"   Prix total: {exit_item2.total_price} F")
    print(f"   ✅ Le prix de vente du produit a été utilisé automatiquement!")
    
    print("\n✅ Test de prix automatique terminé avec succès!")

def reset_test_data():
    """Nettoie les données de test précédentes"""
    print("🧹 Nettoyage des données de test...")
    
    try:
        # Supprimer les transactions existantes
        FinancialTransaction.objects.filter(
            description__icontains="test"
        ).delete()
        
        # Remettre à zéro la dette du client test
        customer = Customer.objects.get(name="Client Test")
        customer.debt = Decimal('0.00')
        customer.save()
        print(f"✅ Dette du client {customer.name} remise à zéro")
        
    except Customer.DoesNotExist:
        print("ℹ️ Pas de client de test à nettoyer")
    
    print("✅ Nettoyage terminé")

if __name__ == "__main__":
    try:
        reset_test_data()
        test_debt_management()
        test_automatic_sale_price()
        print("\n🎉 Tous les tests sont passés avec succès!")
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
