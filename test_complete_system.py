#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GesStockBackend.settings')
django.setup()

from api.models import User, Store, Product, Account, FinancialTransaction
from decimal import Decimal

def test_complete_system():
    print("🧪 Test complet du système avec les nouvelles fonctionnalités")
    
    # Récupérer les données existantes
    store = Store.objects.first()
    user = User.objects.first()
    
    print(f"✅ Store: {store.name}")
    print(f"✅ User: {user.fullname}")
    
    # 1. Test des produits avec prix de vente
    print(f"\n📦 Test des produits avec prix de vente")
    
    product, created = Product.objects.get_or_create(
        reference="PROD-PRICE-TEST",
        defaults={
            'name': "Produit Test Prix",
            'unit': "pièce",
            'sale_price': Decimal('2500.00'),
            'min_stock_alert': 10,
            'store': store
        }
    )
    
    if not created and not product.sale_price:
        product.sale_price = Decimal('2500.00')
        product.save()
    
    print(f"✅ Produit: {product.reference}")
    print(f"✅ Prix de vente: {product.sale_price} FCFA")
    
    # 2. Test des comptes
    print(f"\n💳 Test des comptes pour apports et dépenses")
    
    account, created = Account.objects.get_or_create(
        name="Compte Test Complet",
        account_type="cash",
        store=store,
        defaults={'balance': Decimal('100000.00')}
    )
    
    if created or account.balance < 50000:
        account.balance = Decimal('100000.00')
        account.save()
    
    print(f"✅ Compte: {account.name}")
    print(f"✅ Solde initial: {account.balance} FCFA")
    
    # 3. Test d'un apport de service
    print(f"\n💰 Test d'apport de service")
    
    apport_transaction = FinancialTransaction.objects.create(
        transaction_type='service',
        amount=Decimal('15000.00'),
        to_account=account,  # Compte qui reçoit
        description="Test apport - Prestation de service",
        created_by=user
    )
    
    print(f"✅ Apport créé: {apport_transaction.transaction_number}")
    print(f"✅ Montant: +{apport_transaction.amount} FCFA")
    
    # 4. Test d'une dépense de service
    print(f"\n💸 Test de dépense de service")
    
    depense_transaction = FinancialTransaction.objects.create(
        transaction_type='expense',
        amount=Decimal('8000.00'),
        from_account=account,  # Compte qui paye
        description="Test dépense - Frais de livraison",
        created_by=user
    )
    
    print(f"✅ Dépense créée: {depense_transaction.transaction_number}")
    print(f"✅ Montant: -{depense_transaction.amount} FCFA")
    
    # 5. Vérification des soldes
    account.refresh_from_db()
    expected_balance = Decimal('100000.00') + Decimal('15000.00') - Decimal('8000.00')
    
    print(f"\n📊 Vérification des soldes:")
    print(f"   Solde initial: 100,000 FCFA")
    print(f"   + Apport: +15,000 FCFA")
    print(f"   - Dépense: -8,000 FCFA")
    print(f"   Solde attendu: {expected_balance:,} FCFA")
    print(f"   Solde réel: {account.balance:,} FCFA")
    
    # 6. Vérification des types de transactions
    print(f"\n🔍 Vérification des types de transactions disponibles:")
    for code, display in FinancialTransaction.TRANSACTION_TYPES:
        print(f"   ✅ {code}: {display}")
    
    # 7. Résumé des fonctionnalités
    print(f"\n🎯 Résumé des nouvelles fonctionnalités testées:")
    print(f"   ✅ Produits avec prix de vente: {product.sale_price} FCFA")
    print(f"   ✅ Apports de service: {apport_transaction.get_transaction_type_display()}")
    print(f"   ✅ Dépenses de service: {depense_transaction.get_transaction_type_display()}")
    print(f"   ✅ Gestion automatique des soldes")
    
    if account.balance == expected_balance:
        print(f"\n🎉 Tous les tests sont réussis ! Le système fonctionne parfaitement")
    else:
        print(f"\n❌ Erreur dans les calculs de solde")
    
    print(f"\n📱 Interface utilisateur:")
    print(f"   🌐 Frontend: http://localhost:3001")
    print(f"   📊 Page Comptes: http://localhost:3001/accounts")
    print(f"   💰 Page Transactions: http://localhost:3001/transactions")
    print(f"   📦 Page Produits: http://localhost:3001/products")
    print(f"   🏢 Page Entrepôts: http://localhost:3001/warehouses")
    
    print(f"\n🏁 Test terminé!")

if __name__ == '__main__':
    test_complete_system()
