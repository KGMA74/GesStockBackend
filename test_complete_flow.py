#!/usr/bin/env python
import os
import sys
import django

# Ajouter le répertoire du projet au path
sys.path.append('/home/ryuk/Desktop/gesStock/GesStockBackend')

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GesStockBackend.settings')
django.setup()

from api.models import Account, StockExit, FinancialTransaction, User, Store, Customer, Warehouse, Product, StockExitItem
from decimal import Decimal

def test_stock_exit_with_transaction():
    print("🧪 Test complet : Bon de sortie avec transaction et mise à jour de solde...")
    
    try:
        # Récupérer les objets nécessaires
        store = Store.objects.first()
        user = User.objects.filter(store=store).first()
        account = Account.objects.filter(store=store, is_active=True).first()
        warehouse = Warehouse.objects.filter(store=store).first()
        customer = Customer.objects.filter(store=store).first()
        product = Product.objects.filter(store=store).first()
        
        if not all([store, user, account, warehouse, customer, product]):
            print("❌ Données manquantes pour le test")
            return
        
        print(f"✅ Compte sélectionné: {account.name}")
        print(f"📊 Solde initial: {account.balance}F")
        
        # Compter les transactions initiales
        initial_transactions = FinancialTransaction.objects.count()
        print(f"📊 Transactions initiales: {initial_transactions}")
        
        # Créer un bon de sortie avec compte
        stock_exit = StockExit.objects.create(
            exit_number=f"TEST2-{StockExit.objects.count() + 1:06d}",
            customer=customer,
            warehouse=warehouse,
            account=account,
            total_amount=Decimal('200.00'),
            created_by=user
        )
        
        # Créer un item
        StockExitItem.objects.create(
            stock_exit=stock_exit,
            product=product,
            quantity=2,
            sale_price=Decimal('100.00'),
            total_price=Decimal('200.00')
        )
        
        # Mettre à jour le total
        stock_exit.total_amount = Decimal('200.00')
        stock_exit.save()
        
        print(f"✅ Bon de sortie créé: {stock_exit.exit_number}")
        
        # Vérifier les transactions
        final_transactions = FinancialTransaction.objects.count()
        print(f"📊 Transactions finales: {final_transactions}")
        
        if final_transactions > initial_transactions:
            print(f"✅ Nouvelle transaction créée!")
            
            # Trouver la transaction liée à ce bon de sortie
            transaction = FinancialTransaction.objects.filter(stock_exit=stock_exit).first()
            if transaction:
                print(f"💰 Transaction: {transaction.transaction_number}")
                print(f"💰 Montant: {transaction.amount}F")
                print(f"💰 Type: {transaction.get_transaction_type_display()}")
                print(f"💰 Vers: {transaction.to_account.name if transaction.to_account else 'Aucun compte'}")
        else:
            print("❌ Aucune nouvelle transaction créée")
        
        # Vérifier le solde du compte
        account.refresh_from_db()
        print(f"📊 Nouveau solde: {account.balance}F")
        
        # Vérifier l'historique des transactions du compte
        account_transactions = FinancialTransaction.objects.filter(to_account=account).order_by('-created_at')[:3]
        print(f"\n💳 Historique récent du compte {account.name}:")
        for trans in account_transactions:
            print(f"  - {trans.transaction_number}: +{trans.amount}F ({trans.get_transaction_type_display()})")
            if trans.stock_exit:
                print(f"    Lié au bon de sortie: {trans.stock_exit.exit_number}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stock_exit_with_transaction()
