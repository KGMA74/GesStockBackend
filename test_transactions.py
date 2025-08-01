#!/usr/bin/env python3

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GesStockBackend.settings')
django.setup()

from api.models import (
    User, Store, Account, Customer, Product, Warehouse, 
    StockExit, StockExitItem, FinancialTransaction, ProductStock
)
from decimal import Decimal

def test_financial_transaction_creation():
    print("=== TEST DE CRÉATION DE TRANSACTION FINANCIÈRE ===\n")
    
    # 1. Vérifier les données existantes
    print("1. DONNÉES EXISTANTES:")
    print(f"   - Stores: {Store.objects.count()}")
    print(f"   - Users: {User.objects.count()}")
    print(f"   - Accounts: {Account.objects.count()}")
    print(f"   - Customers: {Customer.objects.count()}")
    print(f"   - Products: {Product.objects.count()}")
    print(f"   - Warehouses: {Warehouse.objects.count()}")
    print(f"   - StockExits: {StockExit.objects.count()}")
    print(f"   - FinancialTransactions: {FinancialTransaction.objects.count()}")
    
    # 2. Afficher les comptes existants
    if Account.objects.exists():
        print("\n2. COMPTES EXISTANTS:")
        for account in Account.objects.all():
            print(f"   - {account.name} ({account.account_type}): {account.balance} F - Store: {account.store.name}")
    
    # 3. Afficher les produits avec stock
    if Product.objects.exists():
        print("\n3. PRODUITS AVEC STOCK:")
        for product in Product.objects.all()[:3]:
            stocks = ProductStock.objects.filter(product=product)
            if stocks.exists():
                for stock in stocks:
                    print(f"   - {product.name} ({product.reference}) - Entrepôt: {stock.warehouse.name} - Stock: {stock.quantity}")
    
    # 4. Afficher les dernières transactions financières
    if FinancialTransaction.objects.exists():
        print("\n4. DERNIÈRES TRANSACTIONS FINANCIÈRES:")
        for transaction in FinancialTransaction.objects.order_by('-created_at')[:3]:
            print(f"   - {transaction.transaction_number}: {transaction.get_transaction_type_display()} - {transaction.amount} F")
            if transaction.to_account:
                print(f"     Vers compte: {transaction.to_account.name}")
            if transaction.stock_exit:
                print(f"     Lié au bon de sortie: {transaction.stock_exit.exit_number}")
    
    print("\n=== FIN DU TEST ===")

if __name__ == '__main__':
    test_financial_transaction_creation()
