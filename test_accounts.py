#!/usr/bin/env python
import os
import sys
import django

# Ajouter le répertoire du projet au path
sys.path.append('/home/ryuk/Desktop/gesStock/GesStockBackend')

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GesStockBackend.settings')
django.setup()

from api.models import Account, StockExit, FinancialTransaction, Store

def test_accounts():
    print("🔧 Test des comptes et transactions...")
    print(f"📊 Nombre de comptes: {Account.objects.count()}")
    print(f"📦 Nombre de bons de sortie: {StockExit.objects.count()}")
    print(f"💰 Nombre de transactions financières: {FinancialTransaction.objects.count()}")
    print(f"🏪 Nombre de boutiques: {Store.objects.count()}")
    
    print("\n💳 Comptes disponibles:")
    for account in Account.objects.all()[:5]:
        print(f"  - {account.name} ({account.get_account_type_display()}) - Solde: {account.balance}F")
    
    print("\n📤 Bons de sortie récents:")
    for exit in StockExit.objects.order_by('-created_at')[:3]:
        account_info = f" → {exit.account.name}" if exit.account else " → Aucun compte"
        print(f"  - {exit.exit_number}: {exit.total_amount}F{account_info}")
    
    print("\n💸 Transactions récentes:")
    for transaction in FinancialTransaction.objects.order_by('-created_at')[:3]:
        account_info = f" → {transaction.to_account.name}" if transaction.to_account else " → Aucun compte"
        print(f"  - {transaction.transaction_type}: {transaction.amount}F{account_info}")

if __name__ == "__main__":
    test_accounts()
