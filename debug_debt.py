#!/usr/bin/env python
"""
Script de debug pour comprendre le problème de dette
"""
import os
import sys
import django
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GesStockBackend.settings')
django.setup()

from api.models import Store, Customer, Product, Warehouse, StockExit, StockExitItem, Account, User, ProductStock

def debug_debt_issue():
    """Debug du problème de dette"""
    print("🔍 Debug du problème de dette")
    print("=" * 40)
    
    # Récupérer les objets
    store = Store.objects.get(name="Boutique Test")
    customer = Customer.objects.get(name="Client Test", store=store)
    warehouse = Warehouse.objects.get(name="Entrepôt Principal", store=store)
    user = User.objects.get(username="admin", store=store)
    product = Product.objects.get(reference="PROD001", store=store)
    account = Account.objects.get(name="Caisse Principale", store=store)
    
    # Remettre à zéro la dette pour un test propre
    customer.debt = Decimal('0.00')
    customer.save()
    
    print(f"📋 État initial du client: {customer.name} - Dette: {customer.debt} F")
    
    # Créer une vente simple
    print("\n1️⃣ Création du bon de sortie...")
    stock_exit = StockExit.objects.create(
        customer=customer,
        warehouse=warehouse,
        account=account,
        created_by=user,
        notes="Test debug"
    )
    print(f"   ✅ Bon créé: {stock_exit.exit_number}")
    print(f"   💰 Montants: total={stock_exit.total_amount}, payé={stock_exit.paid_amount}, restant={stock_exit.remaining_amount}")
    
    customer.refresh_from_db()
    print(f"   👤 Dette client après création: {customer.debt} F")
    
    print("\n2️⃣ Ajout d'un article...")
    old_debt = customer.debt
    exit_item = StockExitItem.objects.create(
        stock_exit=stock_exit,
        product=product,
        quantity=1
    )
    print(f"   ✅ Article ajouté: {exit_item.quantity} x {product.name} = {exit_item.total_price} F")
    
    # Recharger les données
    stock_exit.refresh_from_db()
    customer.refresh_from_db()
    
    print(f"   💰 Montants après ajout: total={stock_exit.total_amount}, payé={stock_exit.paid_amount}, restant={stock_exit.remaining_amount}")
    print(f"   👤 Dette client après ajout: {customer.debt} F")
    print(f"   📈 Augmentation de la dette: {customer.debt - old_debt} F")
    
    print("\n3️⃣ Test de paiement partiel...")
    old_debt = customer.debt
    print(f"   📊 Dette avant paiement: {old_debt} F")
    
    remaining = stock_exit.add_payment(Decimal('400.00'))  # Payer 400 F sur 750 F
    
    customer.refresh_from_db()
    print(f"   👤 Dette client après paiement: {customer.debt} F")
    print(f"   📉 Réduction de la dette: {old_debt - customer.debt} F")
    print(f"   💰 Montant restant à payer: {remaining} F")
    
    print(f"\n✅ Test terminé - Dette finale: {customer.debt} F")

if __name__ == "__main__":
    try:
        debug_debt_issue()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
