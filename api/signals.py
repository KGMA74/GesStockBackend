from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from decimal import Decimal
from .models import (
    StockExit, Invoice, StockEntry, FinancialTransaction, 
    StockEntryItem, StockExitItem
)


@receiver(post_save, sender=StockExit)
def create_invoice_for_stock_exit(sender, instance, created, **kwargs):
    """
    Crée automatiquement une facture pour chaque bon de sortie
    """
    if created:
        Invoice.objects.create(
            stock_exit=instance,
            customer=instance.customer,
            customer_name=instance.customer_name if not instance.customer else None,
            total_amount=instance.total_amount
        )


@receiver(post_save, sender=StockEntry)
def create_financial_transaction_for_purchase(sender, instance, created, **kwargs):
    """
    Crée une transaction financière pour les achats (bons d'entrée)
    et met à jour automatiquement le solde du compte spécifié
    """
    print(f"🚀 Signal déclenché pour StockEntry {instance.entry_number} - created: {created}")
    
    # Créer la transaction si:
    # 1. C'est une nouvelle création ET le montant > 0 (rare car total_amount initialement à 0)
    # 2. OU c'est une mise à jour ET le montant > 0 ET il n'y a pas encore de transaction pour ce bon
    should_create_transaction = False
    
    if created and instance.total_amount > 0:
        should_create_transaction = True
        print("✅ Nouvelle création avec montant > 0")
    elif not created and instance.total_amount > 0:
        # Vérifier s'il n'y a pas déjà une transaction pour ce bon d'entrée
        existing_transaction = FinancialTransaction.objects.filter(
            stock_entry=instance,
            transaction_type='purchase'
        ).exists()
        
        if not existing_transaction:
            should_create_transaction = True
            print("✅ Mise à jour avec montant > 0, pas de transaction existante")
        else:
            print("⏭️ Transaction déjà existante, ignore")
    
    if should_create_transaction:
        supplier_name = instance.supplier.name if instance.supplier else "Fournisseur inconnu"
        print(f"💸 Création d'une transaction d'achat pour {supplier_name} - Montant: {instance.total_amount}")
        
        # Détermine le compte source (d'où sort l'argent)
        from_account = instance.account
        if not from_account:
            print("🔍 Aucun compte spécifié pour l'achat, recherche d'un compte par défaut...")
            # Si aucun compte n'est spécifié, utilise le premier compte de caisse actif de la boutique
            from .models import Account
            from_account = Account.objects.filter(
                store=instance.warehouse.store,
                account_type='cash',
                is_active=True
            ).first()
            
            # Si pas de caisse, utilise le premier compte bancaire actif
            if not from_account:
                from_account = Account.objects.filter(
                    store=instance.warehouse.store,
                    account_type='bank',
                    is_active=True
                ).first()
            
            if from_account:
                print(f"📊 Compte par défaut trouvé: {from_account.name}")
            else:
                print("❌ Aucun compte disponible pour cette boutique!")
        else:
            print(f"✅ Compte spécifié: {from_account.name}")
        
        transaction = FinancialTransaction.objects.create(
    
            transaction_type='purchase',
            amount=instance.total_amount,
            from_account=from_account,  # Le compte qui paye (argent sort)
            stock_entry=instance,
            description=f"Achat auprès de {supplier_name} - Bon {instance.entry_number}",
            created_by=instance.created_by
        )
        
        print(f"✅ Transaction d'achat créée: {transaction.transaction_number}")
        print(f"💰 Nouveau solde du compte {from_account.name}: {from_account.balance}")


@receiver(post_save, sender=StockExit)
def create_financial_transaction_for_sale(sender, instance, created, **kwargs):
    """
    Crée une transaction financière pour les ventes (bons de sortie)
    et met à jour automatiquement le solde du compte spécifié
    """
    print(f"🚀 Signal déclenché pour StockExit {instance.exit_number} - created: {created}")
    
    # Créer la transaction si:
    # 1. C'est une nouvelle création ET le montant > 0 (rare car total_amount initialement à 0)
    # 2. OU c'est une mise à jour ET le montant > 0 ET il n'y a pas encore de transaction pour ce bon
    should_create_transaction = False
    
    if created and instance.total_amount > 0:
        should_create_transaction = True
        print("✅ Nouvelle création avec montant > 0")
    elif not created and instance.total_amount > 0:
        # Vérifier s'il n'y a pas déjà une transaction pour ce bon de sortie
        existing_transaction = FinancialTransaction.objects.filter(
            stock_exit=instance,
            transaction_type='sale'
        ).exists()
        
        if not existing_transaction:
            should_create_transaction = True
            print("✅ Mise à jour avec montant > 0, pas de transaction existante")
        else:
            print("⏭️ Transaction déjà existante, ignore")
    
    if should_create_transaction:
        customer_name = instance.customer.name if instance.customer else instance.customer_name
        print(f"💰 Création d'une transaction financière pour {customer_name} - Montant: {instance.total_amount}")
        
        # Détermine le compte de destination
        to_account = instance.account
        if not to_account:
            print("🔍 Aucun compte spécifié, recherche d'un compte par défaut...")
            # Si aucun compte n'est spécifié, utilise le premier compte de caisse actif de la boutique
            from .models import Account
            to_account = Account.objects.filter(
                store=instance.warehouse.store,
                account_type='cash',
                is_active=True
            ).first()
            
            # Si pas de caisse, utilise le premier compte bancaire actif
            if not to_account:
                to_account = Account.objects.filter(
                    store=instance.warehouse.store,
                    account_type='bank',
                    is_active=True
                ).first()
            
            if to_account:
                print(f"📊 Compte par défaut trouvé: {to_account.name}")
            else:
                print("❌ Aucun compte disponible pour cette boutique!")
        else:
            print(f"✅ Compte spécifié: {to_account.name}")
        
        transaction = FinancialTransaction.objects.create(
            transaction_type='sale',
            amount=instance.total_amount,
            to_account=to_account,  # Le compte qui reçoit l'argent
            stock_exit=instance,
            description=f"Vente à {customer_name} - Bon {instance.exit_number}",
            created_by=instance.created_by
        )
        
        print(f"✅ Transaction financière créée: {transaction.transaction_number}")
        print(f"💰 Nouveau solde du compte {to_account.name}: {to_account.balance}")
        
        # La mise à jour du solde du compte se fait automatiquement 
        # dans la méthode save() de FinancialTransaction


@receiver(pre_save, sender=StockEntry)
def calculate_stock_entry_total(sender, instance, **kwargs):
    """
    Calcule automatiquement le montant total du bon d'entrée
    """
    if instance.pk:
        total = sum(
            item.total_price for item in instance.items.all()
        )
        instance.total_amount = total


@receiver(pre_save, sender=StockExit)
def calculate_stock_exit_total(sender, instance, **kwargs):
    """
    Calcule automatiquement le montant total du bon de sortie
    """
    if instance.pk:
        total = sum(
            item.total_price for item in instance.items.all()
        )
        instance.total_amount = total


@receiver(post_save, sender=StockEntryItem)
def update_stock_entry_total_on_item_change(sender, instance, **kwargs):
    """
    Met à jour le total du bon d'entrée quand un article est modifié
    """
    stock_entry = instance.stock_entry
    total = sum(
        item.total_price for item in stock_entry.items.all()
    )
    if stock_entry.total_amount != total:
        stock_entry.total_amount = total
        stock_entry.save(update_fields=['total_amount'])


@receiver(post_save, sender=StockExitItem)
def update_stock_exit_total_on_item_change(sender, instance, **kwargs):
    """
    Met à jour le total du bon de sortie quand un article est modifié
    """
    stock_exit = instance.stock_exit
    total = sum(
        item.total_price for item in stock_exit.items.all()
    )
    if stock_exit.total_amount != total:
        stock_exit.total_amount = total
        stock_exit.save(update_fields=['total_amount'])
