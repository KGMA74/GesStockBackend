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

def create_test_stock_exit():
    print("🧪 Test de création d'un bon de sortie avec compte...")
    
    # Récupérer les objets nécessaires
    try:
        store = Store.objects.first()
        user = User.objects.filter(store=store).first()
        account = Account.objects.filter(store=store, is_active=True).first()
        warehouse = Warehouse.objects.filter(store=store).first()
        customer = Customer.objects.filter(store=store).first()
        product = Product.objects.filter(store=store).first()
        
        if not all([store, user, account, warehouse, customer, product]):
            print("❌ Données manquantes pour le test")
            return
        
        print(f"✅ Compte sélectionné: {account.name} (Solde initial: {account.balance}F)")
        
        # Créer un bon de sortie avec compte
        stock_exit = StockExit.objects.create(
            exit_number=f"TEST-{StockExit.objects.count() + 1:06d}",
            customer=customer,
            warehouse=warehouse,
            account=account,  # ⭐ Compte associé
            total_amount=Decimal('150.00'),
            created_by=user
        )
        
        # Créer un item
        StockExitItem.objects.create(
            stock_exit=stock_exit,
            product=product,
            quantity=2,
            sale_price=Decimal('75.00'),
            total_price=Decimal('150.00')
        )
        
        # Mettre à jour le total
        stock_exit.total_amount = Decimal('150.00')
        stock_exit.save()
        
        print(f"✅ Bon de sortie créé: {stock_exit.exit_number}")
        
        # Vérifier que le signal a créé la transaction et mis à jour le compte
        account.refresh_from_db()
        print(f"✅ Nouveau solde du compte: {account.balance}F")
        
        # Vérifier la transaction
        transaction = FinancialTransaction.objects.filter(stock_exit=stock_exit).first()
        if transaction:
            print(f"✅ Transaction créée: {transaction.amount}F vers {transaction.to_account.name if transaction.to_account else 'Aucun compte'}")
        else:
            print("❌ Aucune transaction trouvée")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    create_test_stock_exit()
