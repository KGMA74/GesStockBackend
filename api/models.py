from django.db import models
from django.contrib.auth.models import  PermissionsMixin, AbstractBaseUser
from django.core.validators import MinValueValidator
from decimal import Decimal

from .manager import UserManager

class Store(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = "Boutique"
        verbose_name_plural = "Boutiques"
 
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=False, db_index=True)  # Ajout d'un index pour les performances
    phone = models.CharField(max_length=15, null=True, blank=True)
    fullname = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    
    # permissions = models.ManyToManyField('Permission', 
    #     through='UserPermission',
    #     through_fields=('user', 'permission'),  # Spécifie les champs à utiliser
    #     related_name='users',
    #     blank=True
    # )
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  
    is_superuser = models.BooleanField(default=False)  
    
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['fullname']
    
    def __str__(self):
        return f"{self.fullname} ({self.username})"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['store', 'username'],
                name='unique_username_per_store',
                condition=models.Q(store__isnull=False)
            ),
            
            # Cas global (store null) pour le support technique
            models.UniqueConstraint(
                fields=['username'],
                name='unique_username_global',
                condition=models.Q(store__isnull=True)
            ),
        ]
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"


# 🏪 MAGASINS/ENTREPÔTS (lieux physiques de stockage)
class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='warehouses')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.store.name}"
    
    class Meta:
        unique_together = [['name', 'store']]
        verbose_name = "Magasin/Entrepôt"
        verbose_name_plural = "Magasins/Entrepôts"


# 👥 EMPLOYÉS (sans connexion, juste pour suivi)
class Employee(models.Model):
    POSITION_CHOICES = [
        ('vendeur', 'Vendeur'),
        ('caissier', 'Caissier'),
        ('magasinier', 'Magasinier'),
        ('manager', 'Manager'),
        ('autre', 'Autre'),
    ]
    
    fullname = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    hire_date = models.DateField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='employees')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.fullname} - {self.position}"
    
    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"


# 🏢 FOURNISSEURS
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='suppliers')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = [['name', 'store']]
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"


# 👤 CLIENTS
class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='customers')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        unique_together = [['name', 'phone', 'store']]
        verbose_name = "Client"
        verbose_name_plural = "Clients"


# 📦 PRODUITS
class Product(models.Model):
    reference = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=20, default='pièce')  # pièce, kg, litre, etc.
    min_stock_alert = models.PositiveIntegerField(default=5)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.reference} - {self.name}"
    
    def get_total_stock(self):
        """Retourne le stock total du produit dans tous les magasins de la boutique"""
        return self.stocks.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    def get_stock_by_warehouse(self, warehouse):
        """Retourne le stock du produit dans un magasin spécifique"""
        try:
            return self.stocks.get(warehouse=warehouse).quantity
        except ProductStock.DoesNotExist:
            return 0
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"


# 📊 STOCK PAR MAGASIN
class ProductStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stocks')
    quantity = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.reference} - {self.warehouse.name}: {self.quantity}"
    
    class Meta:
        unique_together = [['product', 'warehouse']]
        verbose_name = "Stock Produit"
        verbose_name_plural = "Stocks Produits"


# 💳 COMPTES BANCAIRES ET CAISSE
class Account(models.Model):
    ACCOUNT_TYPES = [
        ('bank', 'Banque'),
        ('cash', 'Caisse'),
    ]
    
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='accounts')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()}) - {self.balance}"
    
    class Meta:
        unique_together = [['name', 'store']]
        verbose_name = "Compte"
        verbose_name_plural = "Comptes"


# 📥 BONS D'ENTRÉE (arrivage stock)
class StockEntry(models.Model):
    entry_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='stock_entries')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_entries')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_stock_entries')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Entrée {self.entry_number} - {self.supplier.name}"
    
    def save(self, *args, **kwargs):
        if not self.entry_number:
            # Génération automatique du numéro d'entrée
            last_entry = StockEntry.objects.filter(
                warehouse__store=self.warehouse.store
            ).order_by('-id').first()
            if last_entry:
                last_number = int(last_entry.entry_number.split('-')[-1])
                self.entry_number = f"ENT-{self.warehouse.store.id}-{last_number + 1:05d}"
            else:
                self.entry_number = f"ENT-{self.warehouse.store.id}-00001"
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Bon d'Entrée"
        verbose_name_plural = "Bons d'Entrée"


# 📥 DÉTAILS DES BONS D'ENTRÉE
class StockEntryItem(models.Model):
    stock_entry = models.ForeignKey(StockEntry, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    total_price = models.DecimalField(max_digits=15, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.purchase_price
        super().save(*args, **kwargs)
        
        # Mise à jour du stock
        stock, created = ProductStock.objects.get_or_create(
            product=self.product,
            warehouse=self.stock_entry.warehouse,
            defaults={'quantity': 0}
        )
        stock.quantity += self.quantity
        stock.save()
    
    def __str__(self):
        return f"{self.product.reference} x{self.quantity}"
    
    class Meta:
        unique_together = [['stock_entry', 'product']]
        verbose_name = "Article Bon d'Entrée"
        verbose_name_plural = "Articles Bons d'Entrée"


# 📤 BONS DE SORTIE (ventes)
class StockExit(models.Model):
    exit_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='stock_exits', blank=True, null=True)
    customer_name = models.CharField(max_length=100, blank=True, null=True)  # Pour clients non enregistrés
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_exits')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_stock_exits')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        customer_display = self.customer.name if self.customer else self.customer_name
        return f"Sortie {self.exit_number} - {customer_display}"
    
    def save(self, *args, **kwargs):
        if not self.exit_number:
            # Génération automatique du numéro de sortie
            last_exit = StockExit.objects.filter(
                warehouse__store=self.warehouse.store
            ).order_by('-id').first()
            if last_exit:
                last_number = int(last_exit.exit_number.split('-')[-1])
                self.exit_number = f"SOR-{self.warehouse.store.id}-{last_number + 1:05d}"
            else:
                self.exit_number = f"SOR-{self.warehouse.store.id}-00001"
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Bon de Sortie"
        verbose_name_plural = "Bons de Sortie"


# 📤 DÉTAILS DES BONS DE SORTIE
class StockExitItem(models.Model):
    stock_exit = models.ForeignKey(StockExit, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    total_price = models.DecimalField(max_digits=15, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.sale_price
        super().save(*args, **kwargs)
        
        # Mise à jour du stock (retrait)
        try:
            stock = ProductStock.objects.get(
                product=self.product,
                warehouse=self.stock_exit.warehouse
            )
            if stock.quantity >= self.quantity:
                stock.quantity -= self.quantity
                stock.save()
            else:
                raise ValueError(f"Stock insuffisant pour {self.product.reference}")
        except ProductStock.DoesNotExist:
            raise ValueError(f"Aucun stock disponible pour {self.product.reference}")
    
    def __str__(self):
        return f"{self.product.reference} x{self.quantity}"
    
    class Meta:
        unique_together = [['stock_exit', 'product']]
        verbose_name = "Article Bon de Sortie"
        verbose_name_plural = "Articles Bons de Sortie"


# 🧾 FACTURES
class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True)
    stock_exit = models.OneToOneField(StockExit, on_delete=models.CASCADE, related_name='invoice')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices', blank=True, null=True)
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        customer_display = self.customer.name if self.customer else self.customer_name
        return f"Facture {self.invoice_number} - {customer_display}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Génération automatique du numéro de facture
            last_invoice = Invoice.objects.filter(
                stock_exit__warehouse__store=self.stock_exit.warehouse.store
            ).order_by('-id').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                self.invoice_number = f"FAC-{self.stock_exit.warehouse.store.id}-{last_number + 1:05d}"
            else:
                self.invoice_number = f"FAC-{self.stock_exit.warehouse.store.id}-00001"
        
        # Synchronisation du montant total avec le bon de sortie
        self.total_amount = self.stock_exit.total_amount
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"


# 💰 MOUVEMENTS DE FONDS
class FinancialTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('purchase', 'Achat (Entrée Stock)'),
        ('sale', 'Vente (Sortie Stock)'),
        ('transfer', 'Transfert entre comptes'),
        ('adjustment', 'Ajustement'),
    ]
    
    transaction_number = models.CharField(max_length=50, unique=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='outgoing_transactions', blank=True, null=True)
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='incoming_transactions', blank=True, null=True)
    
    # Liens vers les documents source
    stock_entry = models.ForeignKey(StockEntry, on_delete=models.CASCADE, related_name='transactions', blank=True, null=True)
    stock_exit = models.ForeignKey(StockExit, on_delete=models.CASCADE, related_name='transactions', blank=True, null=True)
    
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_number} - {self.get_transaction_type_display()}: {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_number:
            # Génération automatique du numéro de transaction
            from datetime import datetime
            today = datetime.now().strftime("%Y%m%d")
            last_transaction = FinancialTransaction.objects.filter(
                transaction_number__startswith=f"TRX-{today}"
            ).order_by('-id').first()
            if last_transaction:
                last_number = int(last_transaction.transaction_number.split('-')[-1])
                self.transaction_number = f"TRX-{today}-{last_number + 1:04d}"
            else:
                self.transaction_number = f"TRX-{today}-0001"
        
        super().save(*args, **kwargs)
        
        # Mise à jour des soldes des comptes
        if self.from_account:
            self.from_account.balance -= self.amount
            self.from_account.save()
        
        if self.to_account:
            self.to_account.balance += self.amount
            self.to_account.save()
    
    class Meta:
        verbose_name = "Transaction Financière"
        verbose_name_plural = "Transactions Financières"
    