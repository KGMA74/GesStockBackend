#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GesStockBackend.settings')
django.setup()

from api.models import User, Store, Account, FinancialTransaction
from decimal import Decimal

def test_expense_transaction():
    print("🧪 Test des transactions de dépenses")
    
    # Récupérer les données existantes
    store = Store.objects.first()
    user = User.objects.first()
    
    # Créer un compte si il n'existe pas
    account, created = Account.objects.get_or_create(
        name="Caisse Test",
        account_type="cash",
        store=store,
        defaults={'balance': Decimal('50000.00')}
    )
    
    if created or account.balance < 10000:
        account.balance = Decimal('50000.00')
        account.save()
    
    print(f"✅ Compte: {account.name}")
    print(f"✅ Solde initial: {account.balance} FCFA")
    
    # Créer une transaction de dépense
    print(f"\n🔄 Création d'une dépense...")
    expense_amount = Decimal('5000.00')
    
    transaction = FinancialTransaction.objects.create(
        transaction_type='expense',
        amount=expense_amount,
        from_account=account,  # Compte qui paye (argent sort)
        description="Test dépense - Frais de transport",
        created_by=user
    )
    
    print(f"✅ Transaction créée: {transaction.transaction_number}")
    print(f"✅ Type: {transaction.get_transaction_type_display()}")
    print(f"✅ Montant: {transaction.amount} FCFA")
    print(f"✅ Description: {transaction.description}")
    
    # Vérifier le solde après dépense
    account.refresh_from_db()
    expected_balance = Decimal('50000.00') - expense_amount
    
    print(f"\n📊 État après dépense:")
    print(f"   Solde attendu: {expected_balance} FCFA")
    print(f"   Solde réel: {account.balance} FCFA")
    
    if account.balance == expected_balance:
        print(f"\n🎉 Test réussi ! La dépense a été correctement enregistrée")
    else:
        print(f"\n❌ Erreur: Le solde ne correspond pas")
        print(f"   Différence: {abs(account.balance - expected_balance)} FCFA")
    
    print(f"\n🏁 Test terminé!")
    print(f"   Transaction ID: {transaction.id}")
    print(f"   Numéro: {transaction.transaction_number}")
    print(f"   Créée le: {transaction.created_at}")

if __name__ == '__main__':
    test_expense_transaction()
