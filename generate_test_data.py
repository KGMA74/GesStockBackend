#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GesStockBackend.settings')
django.setup()

from django.db import transaction
from decimal import Decimal
from datetime import date, datetime, timedelta
import random

from api.models import (
    Store, User, Warehouse, Employee, Supplier, Customer, 
    Product, ProductStock, Account, StockEntry, StockEntryItem,
    StockExit, StockExitItem, Invoice, FinancialTransaction
)

def main():
    print("🏪 Création des données de test pour GesStock...")
    
    with transaction.atomic():
        # Nettoyer les données existantes
        print("\n🧹 Nettoyage des données existantes...")
        models_to_clean = [
            FinancialTransaction, Invoice, StockExitItem, StockExit,
            StockEntryItem, StockEntry, ProductStock, Product,
            Account, Customer, Supplier, Employee, Warehouse, User, Store
        ]
        
        for model in models_to_clean:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                print(f"   ✓ Supprimé {count} {model.__name__}")
        
        # 1. Créer les stores
        print("\n📍 Création des boutiques...")
        store1 = Store.objects.create(
            name='Boutique Centre-Ville',
            description='Boutique principale située au centre-ville'
        )
        print(f"   ✓ {store1.name}")
        
        # 2. Créer les utilisateurs
        print("\n👥 Création des utilisateurs...")
        admin = User.objects.create_user(
            username='test',
            email='test@gesstock.com',
            phone='56182332',
            fullname='test test',
            store=store1,
            is_staff=True,
            is_superuser=True,
            password='test'
        )
        
        manager = User.objects.create_user(
            username='manager',
            email='manager@gesstock.com',
            phone='0123456790',
            fullname='Manager Principal',
            store=store1,
            is_staff=True,
            password='manager123'
        )
        
        vendeur = User.objects.create_user(
            username='vendeur',
            email='vendeur@gesstock.com',
            phone='0123456791',
            fullname='Pierre Vendeur',
            store=store1,
            password='vendeur123'
        )
        
        print(f"   ✓ {admin.fullname} (test/test)")
        print(f"   ✓ {manager.fullname} (manager/manager123)")
        print(f"   ✓ {vendeur.fullname} (vendeur/vendeur123)")
        
        # 3. Créer les entrepôts
        print("\n🏬 Création des entrepôts...")
        warehouse1 = Warehouse.objects.create(
            name='Magasin Principal',
            address='123 Rue du Commerce',
            store=store1
        )
        
        warehouse2 = Warehouse.objects.create(
            name='Entrepôt Stockage',
            address='Zone Industrielle',
            store=store1
        )
        
        print(f"   ✓ {warehouse1.name}")
        print(f"   ✓ {warehouse2.name}")
        
        # 4. Créer les employés
        print("\n👨‍💼 Création des employés...")
        Employee.objects.create(
            fullname='Jean Dupont',
            phone='0123456793',
            position='vendeur',
            salary=Decimal('1800.00'),
            hire_date=date(2023, 6, 15),
            store=store1
        )
        
        Employee.objects.create(
            fullname='Sophie Martin',
            phone='0123456794',
            position='caissier',
            salary=Decimal('1600.00'),
            hire_date=date(2023, 8, 1),
            store=store1
        )
        
        print("   ✓ Jean Dupont (Vendeur)")
        print("   ✓ Sophie Martin (Caissier)")
        
        # 5. Créer les fournisseurs
        print("\n🏢 Création des fournisseurs...")
        supplier1 = Supplier.objects.create(
            name='Distributeur Alimentaire ABC',
            phone='0123456800',
            email='contact@abc-distrib.com',
            address='456 Avenue des Fournisseurs',
            store=store1
        )
        
        supplier2 = Supplier.objects.create(
            name='Grossiste Électronique XYZ',
            phone='0123456801',
            email='ventes@xyz-electronique.com',
            address='789 Boulevard de la Technologie',
            store=store1
        )
        
        print(f"   ✓ {supplier1.name}")
        print(f"   ✓ {supplier2.name}")
        
        # 6. Créer les clients
        print("\n👤 Création des clients...")
        customer1 = Customer.objects.create(
            name='Restaurant Le Bon Goût',
            phone='0123456810',
            email='commandes@lebongout.com',
            address='123 Place du Marché',
            store=store1
        )
        
        customer2 = Customer.objects.create(
            name='Café du Centre',
            phone='0123456811',
            email='cafe@centre.com',
            address='45 Rue Principale',
            store=store1
        )
        
        print(f"   ✓ {customer1.name}")
        print(f"   ✓ {customer2.name}")
        
        # 7. Créer les produits
        print("\n📦 Création des produits...")
        products_data = [
            {
                'reference': 'ALI001',
                'name': 'Riz Basmati 1kg',
                'description': 'Riz basmati de qualité supérieure',
                'unit': 'paquet',
                'min_stock_alert': 10
            },
            {
                'reference': 'ALI002',
                'name': 'Huile de Tournesol 1L',
                'description': 'Huile de tournesol pure',
                'unit': 'bouteille',
                'min_stock_alert': 15
            },
            {
                'reference': 'ALI003',
                'name': 'Sucre Blanc 1kg',
                'description': 'Sucre blanc cristallisé',
                'unit': 'paquet',
                'min_stock_alert': 20
            },
            {
                'reference': 'ELEC001',
                'name': 'Smartphone Galaxy A54',
                'description': 'Smartphone Samsung Galaxy A54 128GB',
                'unit': 'pièce',
                'min_stock_alert': 5
            },
            {
                'reference': 'ELEC002',
                'name': 'Écouteurs Bluetooth',
                'description': 'Écouteurs sans fil Bluetooth 5.0',
                'unit': 'pièce',
                'min_stock_alert': 8
            }
        ]
        
        products = []
        for product_data in products_data:
            product = Product.objects.create(
                **product_data,
                store=store1
            )
            products.append(product)
            print(f"   ✓ {product.reference} - {product.name}")
        
        # 8. Créer les comptes
        print("\n💳 Création des comptes...")
        caisse = Account.objects.create(
            name='Caisse Principale',
            account_type='cash',
            balance=Decimal('5000.00'),
            store=store1
        )
        
        banque = Account.objects.create(
            name='Compte Courant BNP',
            account_type='bank',
            balance=Decimal('25000.00'),
            store=store1
        )
        
        print(f"   ✓ {caisse.name} - {caisse.balance}€")
        print(f"   ✓ {banque.name} - {banque.balance}€")
        
        # 9. Créer les entrées de stock
        print("\n📥 Création des entrées de stock...")
        
        # Entrée 1
        entry1 = StockEntry.objects.create(
            supplier=supplier1,
            warehouse=warehouse1,
            notes='Livraison hebdomadaire - Produits alimentaires',
            created_by=admin,
            created_at=datetime.now() - timedelta(days=7)
        )
        
        # Items pour l'entrée 1
        StockEntryItem.objects.create(
            stock_entry=entry1,
            product=products[0],  # Riz
            quantity=50,
            purchase_price=Decimal('2.50')
        )
        
        StockEntryItem.objects.create(
            stock_entry=entry1,
            product=products[1],  # Huile
            quantity=30,
            purchase_price=Decimal('4.20')
        )
        
        StockEntryItem.objects.create(
            stock_entry=entry1,
            product=products[2],  # Sucre
            quantity=40,
            purchase_price=Decimal('1.80')
        )
        
        entry1.total_amount = Decimal('323.00')  # Calculé manuellement
        entry1.save()
        
        # Entrée 2
        entry2 = StockEntry.objects.create(
            supplier=supplier2,
            warehouse=warehouse1,
            notes='Commande électronique mensuelle',
            created_by=manager,
            created_at=datetime.now() - timedelta(days=3)
        )
        
        StockEntryItem.objects.create(
            stock_entry=entry2,
            product=products[3],  # Smartphone
            quantity=10,
            purchase_price=Decimal('280.00')
        )
        
        StockEntryItem.objects.create(
            stock_entry=entry2,
            product=products[4],  # Écouteurs
            quantity=25,
            purchase_price=Decimal('45.00')
        )
        
        entry2.total_amount = Decimal('3925.00')
        entry2.save()
        
        print(f"   ✓ {entry1.entry_number} - {entry1.total_amount}€")
        print(f"   ✓ {entry2.entry_number} - {entry2.total_amount}€")
        
        # 10. Créer les sorties de stock
        print("\n📤 Création des sorties de stock...")
        
        # Sortie 1
        exit1 = StockExit.objects.create(
            customer=customer1,
            warehouse=warehouse1,
            notes='Commande restaurant - Produits alimentaires',
            created_by=vendeur,
            created_at=datetime.now() - timedelta(days=2)
        )
        
        # Vérifier le stock disponible avant de créer les items
        rice_stock = ProductStock.objects.filter(
            product=products[0], 
            warehouse=warehouse1
        ).first()
        
        if rice_stock and rice_stock.quantity > 0:
            quantity = min(15, rice_stock.quantity)
            StockExitItem.objects.create(
                stock_exit=exit1,
                product=products[0],
                quantity=quantity,
                sale_price=Decimal('3.50')
            )
        
        oil_stock = ProductStock.objects.filter(
            product=products[1], 
            warehouse=warehouse1
        ).first()
        
        if oil_stock and oil_stock.quantity > 0:
            quantity = min(8, oil_stock.quantity)
            StockExitItem.objects.create(
                stock_exit=exit1,
                product=products[1],
                quantity=quantity,
                sale_price=Decimal('5.80')
            )
        
        exit1.total_amount = Decimal('99.00')  # 15*3.50 + 8*5.80
        exit1.save()
        
        # Sortie 2
        exit2 = StockExit.objects.create(
            customer=None,
            customer_name='Client de passage',
            warehouse=warehouse1,
            notes='Vente au comptoir',
            created_by=vendeur,
            created_at=datetime.now() - timedelta(days=1)
        )
        
        phone_stock = ProductStock.objects.filter(
            product=products[3], 
            warehouse=warehouse1
        ).first()
        
        if phone_stock and phone_stock.quantity > 0:
            StockExitItem.objects.create(
                stock_exit=exit2,
                product=products[3],
                quantity=1,
                sale_price=Decimal('399.00')
            )
            
            exit2.total_amount = Decimal('399.00')
            exit2.save()
        
        print(f"   ✓ {exit1.exit_number} - {exit1.total_amount}€")
        print(f"   ✓ {exit2.exit_number} - {exit2.total_amount}€")
        
        # 11. Créer les factures (seulement si elles n'existent pas déjà)
        print("\n🧾 Création des factures...")
        
        # Vérifier si une facture existe déjà pour ces sorties
        if not hasattr(exit1, 'invoice'):
            invoice1 = Invoice.objects.create(
                stock_exit=exit1,
                customer=customer1,
                total_amount=exit1.total_amount
            )
            print(f"   ✓ {invoice1.invoice_number}")
        else:
            print(f"   ✓ Facture déjà existante: {exit1.invoice.invoice_number}")
        
        if not hasattr(exit2, 'invoice'):
            invoice2 = Invoice.objects.create(
                stock_exit=exit2,
                customer_name='Client de passage',
                total_amount=exit2.total_amount
            )
            print(f"   ✓ {invoice2.invoice_number}")
        else:
            print(f"   ✓ Facture déjà existante: {exit2.invoice.invoice_number}")
        
        # 12. Créer les transactions financières
        print("\n💰 Création des transactions financières...")
        
        # Transaction d'achat
        FinancialTransaction.objects.create(
            transaction_type='purchase',
            amount=entry1.total_amount,
            from_account=banque,
            stock_entry=entry1,
            description=f'Paiement fournisseur - {supplier1.name}',
            created_by=admin
        )
        
        # Transaction de vente
        FinancialTransaction.objects.create(
            transaction_type='sale',
            amount=exit1.total_amount,
            to_account=caisse,
            stock_exit=exit1,
            description=f'Encaissement vente - {customer1.name}',
            created_by=vendeur
        )
        
        print("   ✓ Transaction achat créée")
        print("   ✓ Transaction vente créée")
        
        # Afficher les statistiques finales
        print("\n📊 Statistiques des données créées:")
        print(f"   • Boutiques: {Store.objects.count()}")
        print(f"   • Utilisateurs: {User.objects.count()}")
        print(f"   • Entrepôts: {Warehouse.objects.count()}")
        print(f"   • Employés: {Employee.objects.count()}")
        print(f"   • Fournisseurs: {Supplier.objects.count()}")
        print(f"   • Clients: {Customer.objects.count()}")
        print(f"   • Produits: {Product.objects.count()}")
        print(f"   • Comptes: {Account.objects.count()}")
        print(f"   • Entrées de stock: {StockEntry.objects.count()}")
        print(f"   • Sorties de stock: {StockExit.objects.count()}")
        print(f"   • Factures: {Invoice.objects.count()}")
        print(f"   • Transactions: {FinancialTransaction.objects.count()}")
        
        print("\n✅ Données de test créées avec succès!")
        print("\n🔑 Comptes de connexion:")
        print("   • Admin: test / test")
        print("   • Manager: manager / manager123") 
        print("   • Vendeur: vendeur / vendeur123")

if __name__ == '__main__':
    main()
