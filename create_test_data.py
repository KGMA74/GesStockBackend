#!/usr/bin/env python
"""
Script de génération de données de test pour le système de gestion de stock

Usage:
    python manage.py shell < create_test_data.py
"""

from django.contrib.auth import get_user_model
from api.models import (
    Store, Warehouse, User, Employee, Supplier, Customer, Product, 
    ProductStock, Account, StockEntry, StockEntryItem, StockExit, StockExitItem
)
from decimal import Decimal
from datetime import date, datetime, timedelta

User = get_user_model()

def create_test_data():
    print("🏪 Création des données de test...")
    
    # 1. Création des boutiques
    print("\n1. Création des boutiques...")
    store1 = Store.objects.create(
        name="Boutique Centre-Ville",
        description="Magasin principal au centre-ville"
    )
    
    store2 = Store.objects.create(
        name="Boutique Banlieue",
        description="Succursale en banlieue"
    )
    
    # 2. Création d'un super admin
    print("\n2. Création du super admin...")
    super_admin = User.objects.create_user(
        username="admin",
        fullname="Administrateur Système",
        is_staff=True,
        is_superuser=True,
        store=None  # Super admin global
    )
    super_admin.set_password("admin123")
    super_admin.save()
    
    # 3. Création des utilisateurs de boutique
    print("\n3. Création des utilisateurs de boutique...")
    user1 = User.objects.create_user(
        username="manager1",
        fullname="Manager Centre-Ville",
        phone="123456789",
        store=store1,
        is_staff=True
    )
    user1.set_password("manager123")
    user1.save()
    
    user2 = User.objects.create_user(
        username="vendeur1",
        fullname="Vendeur Centre-Ville",
        phone="987654321",
        store=store1
    )
    user2.set_password("vendeur123")
    user2.save()
    
    # 4. Création des magasins/entrepôts
    print("\n4. Création des magasins/entrepôts...")
    warehouse1_main = Warehouse.objects.create(
        name="Magasin Principal",
        address="123 Rue Principale",
        store=store1
    )
    
    warehouse1_depot = Warehouse.objects.create(
        name="Dépôt",
        address="456 Rue du Dépôt",
        store=store1
    )
    
    # 5. Création des employés
    print("\n5. Création des employés...")
    Employee.objects.create(
        fullname="Jean Dupont",
        phone="111222333",
        position="vendeur",
        salary=Decimal("1500.00"),
        hire_date=date(2024, 1, 15),
        store=store1
    )
    
    Employee.objects.create(
        fullname="Marie Martin",
        phone="444555666",
        position="caissier",
        salary=Decimal("1400.00"),
        hire_date=date(2024, 3, 1),
        store=store1
    )
    
    # 6. Création des fournisseurs
    print("\n6. Création des fournisseurs...")
    supplier1 = Supplier.objects.create(
        name="Grossiste ABC",
        phone="777888999",
        email="contact@grossiste-abc.com",
        address="789 Avenue des Grossistes",
        store=store1
    )
    
    supplier2 = Supplier.objects.create(
        name="Import Export XYZ",
        phone="101112131",
        email="info@xyz-import.com",
        store=store1
    )
    
    # 7. Création des clients
    print("\n7. Création des clients...")
    customer1 = Customer.objects.create(
        name="Restaurant Le Bon Goût",
        phone="141516171",
        email="commande@bongoût.com",
        address="321 Rue des Restaurants",
        store=store1
    )
    
    customer2 = Customer.objects.create(
        name="Épicerie du Coin",
        phone="181920212",
        email="achats@epicerie-coin.com",
        store=store1
    )
    
    # 8. Création des produits
    print("\n8. Création des produits...")
    products_data = [
        {"ref": "PROD001", "name": "Riz Basmati 5kg", "unit": "sac", "min_stock": 10},
        {"ref": "PROD002", "name": "Huile d'Olive 1L", "unit": "bouteille", "min_stock": 20},
        {"ref": "PROD003", "name": "Pâtes Italiennes 500g", "unit": "paquet", "min_stock": 30},
        {"ref": "PROD004", "name": "Sucre Blanc 1kg", "unit": "paquet", "min_stock": 15},
        {"ref": "PROD005", "name": "Café Arabica 250g", "unit": "paquet", "min_stock": 25},
    ]
    
    products = []
    for prod_data in products_data:
        product = Product.objects.create(
            reference=prod_data["ref"],
            name=prod_data["name"],
            unit=prod_data["unit"],
            min_stock_alert=prod_data["min_stock"],
            store=store1
        )
        products.append(product)
        
        # Initialisation du stock à zéro pour chaque magasin
        ProductStock.objects.create(
            product=product,
            warehouse=warehouse1_main,
            quantity=0
        )
        ProductStock.objects.create(
            product=product,
            warehouse=warehouse1_depot,
            quantity=0
        )
    
    # 9. Création des comptes
    print("\n9. Création des comptes...")
    account_bank = Account.objects.create(
        name="Compte Bancaire Principal",
        account_type="bank",
        balance=Decimal("50000.00"),
        store=store1
    )
    
    account_cash = Account.objects.create(
        name="Caisse Principale",
        account_type="cash",
        balance=Decimal("2000.00"),
        store=store1
    )
    
    # 10. Création des bons d'entrée (achats)
    print("\n10. Création des bons d'entrée...")
    
    # Premier bon d'entrée
    entry1 = StockEntry.objects.create(
        supplier=supplier1,
        warehouse=warehouse1_depot,
        notes="Première commande de stock",
        created_by=user1
    )
    
    # Articles du premier bon
    entry_items_data = [
        {"product": products[0], "qty": 50, "price": Decimal("8.50")},  # Riz
        {"product": products[1], "qty": 100, "price": Decimal("4.20")}, # Huile
        {"product": products[2], "qty": 200, "price": Decimal("1.80")}, # Pâtes
    ]
    
    for item_data in entry_items_data:
        StockEntryItem.objects.create(
            stock_entry=entry1,
            product=item_data["product"],
            quantity=item_data["qty"],
            purchase_price=item_data["price"]
        )
    
    # Deuxième bon d'entrée
    entry2 = StockEntry.objects.create(
        supplier=supplier2,
        warehouse=warehouse1_depot,
        notes="Commande complémentaire",
        created_by=user1
    )
    
    StockEntryItem.objects.create(
        stock_entry=entry2,
        product=products[3],  # Sucre
        quantity=80,
        purchase_price=Decimal("2.10")
    )
    
    StockEntryItem.objects.create(
        stock_entry=entry2,
        product=products[4],  # Café
        quantity=60,
        purchase_price=Decimal("12.00")
    )
    
    # 11. Transfert de stock vers le magasin principal
    print("\n11. Transfert vers le magasin principal...")
    
    # Simuler un transfert manuel en modifiant les stocks
    transfers = [
        {"product": products[0], "qty": 30},  # 30 sacs de riz
        {"product": products[1], "qty": 60},  # 60 bouteilles d'huile
        {"product": products[2], "qty": 120}, # 120 paquets de pâtes
        {"product": products[3], "qty": 50},  # 50 paquets de sucre
        {"product": products[4], "qty": 40},  # 40 paquets de café
    ]
    
    for transfer in transfers:
        # Retirer du dépôt
        depot_stock = ProductStock.objects.get(
            product=transfer["product"],
            warehouse=warehouse1_depot
        )
        depot_stock.quantity -= transfer["qty"]
        depot_stock.save()
        
        # Ajouter au magasin principal
        main_stock = ProductStock.objects.get(
            product=transfer["product"],
            warehouse=warehouse1_main
        )
        main_stock.quantity += transfer["qty"]
        main_stock.save()
    
    # 12. Création des bons de sortie (ventes)
    print("\n12. Création des bons de sortie...")
    
    # Première vente
    exit1 = StockExit.objects.create(
        customer=customer1,
        warehouse=warehouse1_main,
        notes="Commande restaurant",
        created_by=user2
    )
    
    StockExitItem.objects.create(
        stock_exit=exit1,
        product=products[0],  # Riz
        quantity=5,
        sale_price=Decimal("12.00")
    )
    
    StockExitItem.objects.create(
        stock_exit=exit1,
        product=products[1],  # Huile
        quantity=10,
        sale_price=Decimal("6.50")
    )
    
    # Deuxième vente
    exit2 = StockExit.objects.create(
        customer=customer2,
        warehouse=warehouse1_main,
        notes="Réassort épicerie",
        created_by=user2
    )
    
    StockExitItem.objects.create(
        stock_exit=exit2,
        product=products[2],  # Pâtes
        quantity=30,
        sale_price=Decimal("2.50")
    )
    
    StockExitItem.objects.create(
        stock_exit=exit2,
        product=products[4],  # Café
        quantity=8,
        sale_price=Decimal("18.00")
    )
    
    # Vente à un client non enregistré
    exit3 = StockExit.objects.create(
        customer_name="Client Passage",
        warehouse=warehouse1_main,
        notes="Vente au comptoir",
        created_by=user2
    )
    
    StockExitItem.objects.create(
        stock_exit=exit3,
        product=products[3],  # Sucre
        quantity=3,
        sale_price=Decimal("3.20")
    )
    
    print("\n✅ Données de test créées avec succès !")
    print("\n📊 Résumé des données créées :")
    print(f"   - Boutiques : {Store.objects.count()}")
    print(f"   - Utilisateurs : {User.objects.count()}")
    print(f"   - Magasins/Entrepôts : {Warehouse.objects.count()}")
    print(f"   - Employés : {Employee.objects.count()}")
    print(f"   - Fournisseurs : {Supplier.objects.count()}")
    print(f"   - Clients : {Customer.objects.count()}")
    print(f"   - Produits : {Product.objects.count()}")
    print(f"   - Comptes : {Account.objects.count()}")
    print(f"   - Bons d'entrée : {StockEntry.objects.count()}")
    print(f"   - Bons de sortie : {StockExit.objects.count()}")
    print(f"   - Factures : {Invoice.objects.count()}")
    
    print("\n🔑 Comptes de connexion créés :")
    print("   Super Admin:")
    print("     Username: admin")
    print("     Password: admin123")
    print("   Manager Boutique:")
    print("     Username: manager1") 
    print("     Password: manager123")
    print("   Vendeur:")
    print("     Username: vendeur1")
    print("     Password: vendeur123")

if __name__ == "__main__":
    create_test_data()
