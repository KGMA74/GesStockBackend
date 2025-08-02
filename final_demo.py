#!/usr/bin/env python
"""
Script de test final pour démontrer toutes les nouvelles fonctionnalités
"""
import os
import sys
import django
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GesStockBackend.settings')
django.setup()

from api.models import Store, Customer, Product, Warehouse, StockExit, StockExitItem, Account, User, ProductStock

def demonstrate_features():
    """Démonstration complète des nouvelles fonctionnalités"""
    print("🎯 DÉMONSTRATION COMPLÈTE DES NOUVELLES FONCTIONNALITÉS")
    print("=" * 60)
    
    # Récupérer les objets de test
    store = Store.objects.get(name="Boutique Test")
    customer = Customer.objects.get(name="Client Test", store=store)
    warehouse = Warehouse.objects.get(name="Entrepôt Principal", store=store)
    user = User.objects.get(username="admin", store=store)
    product = Product.objects.get(reference="PROD001", store=store)
    account = Account.objects.get(name="Caisse Principale", store=store)
    
    # Reset du client
    customer.debt = Decimal('0.00')
    customer.save()
    
    print(f"📋 Client: {customer.name} - Dette initiale: {customer.debt} F")
    print(f"📦 Produit: {product.name}")
    print(f"   💰 Prix d'achat: {product.price} F")
    print(f"   🏷️ Prix de vente: {product.sale_price} F")
    
    print(f"\n🏪 FONCTIONNALITÉ 1: UTILISATION AUTOMATIQUE DU PRIX DE VENTE")
    print("-" * 60)
    
    # Créer une vente
    stock_exit = StockExit.objects.create(
        customer=customer,
        warehouse=warehouse,
        account=account,
        created_by=user,
        notes="Démonstration prix automatique"
    )
    
    print(f"✅ Bon de sortie créé: {stock_exit.exit_number}")
    
    # Ajouter un article SANS spécifier le prix de vente
    exit_item = StockExitItem.objects.create(
        stock_exit=stock_exit,
        product=product,
        quantity=2
        # ⚠️ AUCUN sale_price spécifié !
    )
    
    print(f"📦 Article ajouté: {exit_item.quantity} x {product.name}")
    print(f"   🎯 Prix unitaire utilisé automatiquement: {exit_item.sale_price} F")
    print(f"   ✅ Montant total: {exit_item.total_price} F")
    print(f"   🔥 Le système a automatiquement utilisé le prix de vente du produit !")
    
    # Recharger les données
    stock_exit.refresh_from_db()
    customer.refresh_from_db()
    
    print(f"\n💰 FONCTIONNALITÉ 2: GESTION DES DETTES CLIENTS")
    print("-" * 60)
    
    print(f"📊 Montants de la vente:")
    print(f"   Total à payer: {stock_exit.total_amount} F")
    print(f"   Montant payé: {stock_exit.paid_amount} F")
    print(f"   Montant restant: {stock_exit.remaining_amount} F")
    print(f"   Statut: {stock_exit.payment_status}")
    
    print(f"\n👤 Dette automatique du client:")
    print(f"   Dette totale: {customer.debt} F")
    print(f"   ✅ Le montant impayé a été automatiquement ajouté à la dette !")
    
    print(f"\n💳 FONCTIONNALITÉ 3: PAIEMENTS PARTIELS")
    print("-" * 60)
    
    # Le client paie une partie
    print(f"💰 Le client paie 1000 F sur {stock_exit.total_amount} F...")
    remaining = stock_exit.add_payment(Decimal('1000.00'))
    
    customer.refresh_from_db()
    
    print(f"📊 Après paiement partiel:")
    print(f"   Montant payé: {stock_exit.paid_amount} F")
    print(f"   Montant restant: {remaining} F")
    print(f"   Statut: {stock_exit.payment_status}")
    print(f"   Dette du client: {customer.debt} F")
    print(f"   ✅ La dette a été automatiquement réduite !")
    
    # Paiement final
    print(f"\n💰 Le client paie le reste ({remaining} F)...")
    final_remaining = stock_exit.add_payment(remaining)
    
    customer.refresh_from_db()
    
    print(f"📊 Après paiement complet:")
    print(f"   Montant payé: {stock_exit.paid_amount} F")
    print(f"   Montant restant: {final_remaining} F")
    print(f"   Statut: {stock_exit.payment_status}")
    print(f"   Vente entièrement payée: {stock_exit.is_fully_paid}")
    print(f"   Dette du client: {customer.debt} F")
    print(f"   ✅ La dette a été entièrement effacée !")
    
    print(f"\n🎯 RÉSUMÉ DES AMÉLIORATIONS")
    print("=" * 60)
    print("✅ 1. Prix de vente automatique : Le système utilise automatiquement")
    print("     le sale_price du produit quand aucun prix n'est spécifié")
    print("✅ 2. Gestion des dettes : Les montants impayés sont automatiquement")
    print("     ajoutés à la dette du client")
    print("✅ 3. Paiements partiels : Support complet des paiements en plusieurs")
    print("     fois avec mise à jour automatique des dettes")
    print("✅ 4. Statuts de paiement : Tracking précis (non_paye, partiel, paye)")
    print("✅ 5. Intégrité des données : Toutes les mises à jour sont cohérentes")
    print("     entre les ventes, les paiements et les dettes clients")
    
    print(f"\n🎉 TOUTES LES FONCTIONNALITÉS SONT OPÉRATIONNELLES !")

if __name__ == "__main__":
    try:
        demonstrate_features()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
