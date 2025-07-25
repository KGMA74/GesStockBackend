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
    """
    if created and instance.total_amount > 0:
        # Pour les achats, on peut créer une transaction sans compte spécifique
        # L'utilisateur devra ensuite spécifier le compte utilisé
        FinancialTransaction.objects.create(
            transaction_type='purchase',
            amount=instance.total_amount,
            stock_entry=instance,
            description=f"Achat auprès de {instance.supplier.name} - Bon {instance.entry_number}",
            created_by=instance.created_by
        )


@receiver(post_save, sender=StockExit)
def create_financial_transaction_for_sale(sender, instance, created, **kwargs):
    """
    Crée une transaction financière pour les ventes (bons de sortie)
    """
    if created and instance.total_amount > 0:
        customer_name = instance.customer.name if instance.customer else instance.customer_name
        FinancialTransaction.objects.create(
            transaction_type='sale',
            amount=instance.total_amount,
            stock_exit=instance,
            description=f"Vente à {customer_name} - Bon {instance.exit_number}",
            created_by=instance.created_by
        )


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
