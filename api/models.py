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
    email = models.EmailField(max_length=254)
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
    REQUIRED_FIELDS = ['fullname', 'email']
    
    def __str__(self):
        return f"{self.fullname} ({self.username})"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['store', 'username'],
                name='unique_username_per_store',
                condition=models.Q(store__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['store', 'email'],
                name='unique_email_per_store',
                condition=models.Q(store__isnull=False)
            ),
            
            
            # Cas global (store null) pour le support technique
            models.UniqueConstraint(
                fields=['username'],
                name='unique_username_global',
                condition=models.Q(store__isnull=True)
            ),
            models.UniqueConstraint(
                fields=['email'],
                name='unique_email_global',
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
    debt = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])  # Montant dû par le client
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='customers')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - Dette: {self.debt} F"
    
    def add_debt(self, amount):
        """Ajouter une dette au client"""
        self.debt += amount
        self.save()
    
    def pay_debt(self, amount):
        """Payer une partie ou la totalité de la dette"""
        if amount > self.debt:
            raise ValueError(f"Le montant payé ({amount}) ne peut pas être supérieur à la dette ({self.debt})")
        self.debt -= amount
        self.save()
        return self.debt  # Retourne la dette restante
    
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
    price = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))  # Prix d'achat
    sale_price = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))  # Prix de vente
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
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='stock_entries', blank=True, null=True)  # Compte source pour le paiement
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
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='stock_exits', blank=True, null=True)  # Compte de destination des encaissements
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))  # Montant total à payer
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))  # Montant payé par le client
    remaining_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))  # Montant restant dû
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_stock_exits')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        customer_display = self.customer.name if self.customer else self.customer_name
        return f"Sortie {self.exit_number} - {customer_display}"
    
    def save(self, *args, **kwargs):
        # Éviter la mise à jour automatique de la dette si on utilise add_payment
        skip_debt_update = kwargs.pop('skip_debt_update', False)
        
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
        
        # Calculer le montant restant
        old_remaining = Decimal('0.00')
        if self.pk and not skip_debt_update:
            # Obtenir l'ancienne valeur pour calculer la différence
            try:
                old_instance = StockExit.objects.get(pk=self.pk)
                old_remaining = old_instance.remaining_amount
            except StockExit.DoesNotExist:
                pass
        
        self.remaining_amount = self.total_amount - self.paid_amount
        
        # Si il y a un client enregistré, gérer sa dette (sauf si explicitement évité)
        if self.customer and not skip_debt_update:
            debt_difference = self.remaining_amount - old_remaining
            if debt_difference != 0:
                self.customer.debt += debt_difference
                self.customer.save()
        
        super().save(*args, **kwargs)
    
    def add_payment(self, amount):
        """Ajouter un paiement à cette vente"""
        if amount <= 0:
            raise ValueError("Le montant du paiement doit être positif")
        
        if self.paid_amount + amount > self.total_amount:
            raise ValueError(f"Le paiement total ne peut pas dépasser le montant dû. Montant restant: {self.remaining_amount} F")
        
        old_remaining = self.remaining_amount
        self.paid_amount += amount
        self.remaining_amount = self.total_amount - self.paid_amount
        
        # Réduire la dette du client si applicable
        if self.customer and amount > 0:
            debt_reduction = old_remaining - self.remaining_amount
            self.customer.debt -= debt_reduction
            self.customer.save()
        
        self.save(skip_debt_update=True)  # Éviter la double mise à jour de la dette
        return self.remaining_amount
    
    @property
    def is_fully_paid(self):
        """Vérifier si la vente est entièrement payée"""
        return self.remaining_amount <= Decimal('0.00')
    
    @property
    def payment_status(self):
        """Statut du paiement"""
        if self.paid_amount <= Decimal('0.00'):
            return 'non_paye'
        elif self.remaining_amount <= Decimal('0.00'):
            return 'paye'
        else:
            return 'partiel'
    
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
        # Si le prix de vente n'est pas défini, utiliser le sale_price du produit
        if not self.sale_price or self.sale_price == Decimal('0.00'):
            self.sale_price = self.product.sale_price
        
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
                raise ValueError(f"Stock insuffisant pour {self.product.reference}. Stock disponible: {stock.quantity}, quantité demandée: {self.quantity}")
        except ProductStock.DoesNotExist:
            raise ValueError(f"Aucun stock disponible pour {self.product.reference} dans l'entrepôt {self.stock_exit.warehouse.name}")
    
    def __str__(self):
        return f"{self.product.reference} x{self.quantity} à {self.sale_price} F/u"
    
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
        ('service', 'Apport (Prestation de service)'),
        ('expense', 'Dépense (Frais divers)'),
        ('debt_payment', 'Remboursement de dette'),
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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='debt_payments', blank=True, null=True)
    
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
        
        # Mise à jour des soldes des comptes avec vérification
        if self.from_account:
            if self.from_account.balance < self.amount:
                raise ValueError(f"Solde insuffisant dans le compte '{self.from_account.name}'. Solde disponible: {self.from_account.balance} F, montant demandé: {self.amount} F")
            self.from_account.balance -= self.amount
            self.from_account.save()
        
        if self.to_account:
            self.to_account.balance += self.amount
            self.to_account.save()
    
    class Meta:
        verbose_name = "Transaction Financière"
        verbose_name_plural = "Transactions Financières"


# 🔄 TRANSFERTS DE STOCK
class StockTransfer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ]
    
    transfer_number = models.CharField(max_length=50, unique=True)
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='outgoing_transfers')
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='incoming_transfers')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_transfers')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Transfert {self.transfer_number} - {self.from_warehouse.name} → {self.to_warehouse.name}"
    
    def save(self, *args, **kwargs):
        if not self.transfer_number:
            # Génération automatique du numéro de transfert
            last_transfer = StockTransfer.objects.filter(
                from_warehouse__store=self.from_warehouse.store
            ).order_by('-id').first()
            if last_transfer:
                last_number = int(last_transfer.transfer_number.split('-')[-1])
                self.transfer_number = f"TRF-{self.from_warehouse.store.id}-{last_number + 1:05d}"
            else:
                self.transfer_number = f"TRF-{self.from_warehouse.store.id}-00001"
        super().save(*args, **kwargs)
    
    def complete_transfer(self):
        """Marquer le transfert comme terminé et mettre à jour les stocks"""
        if self.status != 'pending':
            raise ValueError("Seuls les transferts en attente peuvent être terminés")
        
        from django.utils import timezone
        
        # Mettre à jour les stocks pour chaque article
        for item in self.items.all():
            # Retirer du stock source
            source_stock = ProductStock.objects.get(
                product=item.product,
                warehouse=self.from_warehouse
            )
            if source_stock.quantity < item.quantity:
                raise ValueError(f"Stock insuffisant pour {item.product.reference} dans {self.from_warehouse.name}")
            
            source_stock.quantity -= item.quantity
            source_stock.save()
            
            # Ajouter au stock destination
            dest_stock, created = ProductStock.objects.get_or_create(
                product=item.product,
                warehouse=self.to_warehouse,
                defaults={'quantity': 0}
            )
            dest_stock.quantity += item.quantity
            dest_stock.save()
        
        # Marquer comme terminé
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    class Meta:
        verbose_name = "Transfert de Stock"
        verbose_name_plural = "Transferts de Stock"


# 🔄 ARTICLES DES TRANSFERTS
class StockTransferItem(models.Model):
    stock_transfer = models.ForeignKey(StockTransfer, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    
    def save(self, *args, **kwargs):
        # Vérifier que le transfert n'est pas encore terminé
        if self.stock_transfer.status == 'completed':
            raise ValueError("Impossible de modifier un transfert terminé")
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.reference} x{self.quantity} - {self.stock_transfer.transfer_number}"
    
    class Meta:
        unique_together = [['stock_transfer', 'product']]
        verbose_name = "Article de Transfert"
        verbose_name_plural = "Articles de Transfert"
    