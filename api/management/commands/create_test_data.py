from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import (
    Store, Warehouse, Employee, Supplier, Customer, Product, 
    ProductStock, Account, StockEntry, StockEntryItem, StockExit, StockExitItem
)
from decimal import Decimal
from datetime import date

User = get_user_model()


class Command(BaseCommand):
    help = 'Crée des données de test pour le système de gestion de stock'

    def handle(self, *args, **options):
        self.stdout.write("🏪 Création des données de test...")
        
        # 1. Création des boutiques
        self.stdout.write("\n1. Création des boutiques...")
        store1, created = Store.objects.get_or_create(
            name="Boutique Centre-Ville",
            defaults={"description": "Magasin principal au centre-ville"}
        )
        
        # 2. Création d'un super admin
        self.stdout.write("\n2. Création du super admin...")
        if not User.objects.filter(username="admin").exists():
            super_admin = User.objects.create_user(
                username="admin",
                fullname="Administrateur Système",
                is_staff=True,
                is_superuser=True,
                store=None
            )
            super_admin.set_password("admin123")
            super_admin.save()
        
        # 3. Création des utilisateurs de boutique
        self.stdout.write("\n3. Création des utilisateurs de boutique...")
        if not User.objects.filter(username="manager1").exists():
            user1 = User.objects.create_user(
                username="manager1",
                fullname="Manager Centre-Ville",
                phone="123456789",
                store=store1,
                is_staff=True
            )
            user1.set_password("manager123")
            user1.save()
        else:
            user1 = User.objects.get(username="manager1")
        
        # 4. Création des magasins/entrepôts
        self.stdout.write("\n4. Création des magasins/entrepôts...")
        warehouse1_main, created = Warehouse.objects.get_or_create(
            name="Magasin Principal",
            store=store1,
            defaults={"address": "123 Rue Principale"}
        )
        
        warehouse1_depot, created = Warehouse.objects.get_or_create(
            name="Dépôt",
            store=store1,
            defaults={"address": "456 Rue du Dépôt"}
        )
        
        # 5. Création des employés
        self.stdout.write("\n5. Création des employés...")
        Employee.objects.get_or_create(
            fullname="Jean Dupont",
            store=store1,
            defaults={
                "phone": "111222333",
                "position": "vendeur",
                "salary": Decimal("1500.00"),
                "hire_date": date(2024, 1, 15)
            }
        )
        
        # 6. Création des fournisseurs
        self.stdout.write("\n6. Création des fournisseurs...")
        supplier1, created = Supplier.objects.get_or_create(
            name="Grossiste ABC",
            store=store1,
            defaults={
                "phone": "777888999",
                "email": "contact@grossiste-abc.com",
                "address": "789 Avenue des Grossistes"
            }
        )
        
        # 7. Création des clients
        self.stdout.write("\n7. Création des clients...")
        customer1, created = Customer.objects.get_or_create(
            name="Restaurant Le Bon Goût",
            store=store1,
            defaults={
                "phone": "141516171",
                "email": "commande@bongoût.com",
                "address": "321 Rue des Restaurants"
            }
        )
        
        # 8. Création des produits
        self.stdout.write("\n8. Création des produits...")
        products_data = [
            {"ref": "PROD001", "name": "Riz Basmati 5kg", "unit": "sac", "min_stock": 10},
            {"ref": "PROD002", "name": "Huile d'Olive 1L", "unit": "bouteille", "min_stock": 20},
            {"ref": "PROD003", "name": "Pâtes Italiennes 500g", "unit": "paquet", "min_stock": 30},
        ]
        
        products = []
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                reference=prod_data["ref"],
                defaults={
                    "name": prod_data["name"],
                    "unit": prod_data["unit"],
                    "min_stock_alert": prod_data["min_stock"],
                    "store": store1
                }
            )
            products.append(product)
            
            # Initialisation du stock
            ProductStock.objects.get_or_create(
                product=product,
                warehouse=warehouse1_main,
                defaults={"quantity": 0}
            )
            ProductStock.objects.get_or_create(
                product=product,
                warehouse=warehouse1_depot,
                defaults={"quantity": 0}
            )
        
        # 9. Création des comptes
        self.stdout.write("\n9. Création des comptes...")
        Account.objects.get_or_create(
            name="Compte Bancaire Principal",
            store=store1,
            defaults={
                "account_type": "bank",
                "balance": Decimal("50000.00")
            }
        )
        
        Account.objects.get_or_create(
            name="Caisse Principale",
            store=store1,
            defaults={
                "account_type": "cash",
                "balance": Decimal("2000.00")
            }
        )
        
        # 10. Création d'un bon d'entrée
        self.stdout.write("\n10. Création d'un bon d'entrée...")
        if not StockEntry.objects.filter(supplier=supplier1).exists():
            entry1 = StockEntry.objects.create(
                supplier=supplier1,
                warehouse=warehouse1_depot,
                notes="Première commande de stock",
                created_by=user1
            )
            
            # Articles du bon
            StockEntryItem.objects.create(
                stock_entry=entry1,
                product=products[0],
                quantity=50,
                purchase_price=Decimal("8.50")
            )
            
            StockEntryItem.objects.create(
                stock_entry=entry1,
                product=products[1],
                quantity=100,
                purchase_price=Decimal("4.20")
            )
        
        self.stdout.write("\n✅ Données de test créées avec succès !")
        self.stdout.write(self.style.SUCCESS("\n🔑 Comptes de connexion :"))
        self.stdout.write("   Super Admin: admin / admin123")
        self.stdout.write("   Manager: manager1 / manager123")
