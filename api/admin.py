from unfold import admin
from .models import (
    User, Store, Warehouse, Employee, Supplier, Customer, Product, ProductStock,
    StockEntry, StockEntryItem, StockExit, StockExitItem, Invoice, Account, FinancialTransaction
)


# Configuration Admin pour Store
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


# Configuration Admin pour User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'fullname', 'store', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff', 'store']
    search_fields = ['username', 'fullname', 'phone']
    readonly_fields = ['created_at']


# Configuration Admin pour Warehouse
@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'is_active']
    list_filter = ['is_active', 'store']
    search_fields = ['name']


# Configuration Admin pour Employee
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['fullname', 'position', 'store', 'salary', 'hire_date', 'is_active']
    list_filter = ['position', 'is_active', 'store', 'hire_date']
    search_fields = ['fullname', 'phone']
    date_hierarchy = 'hire_date'


# Configuration Admin pour Supplier
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'phone', 'is_active']
    list_filter = ['is_active', 'store']
    search_fields = ['name', 'phone', 'email']


# Configuration Admin pour Customer
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'store', 'phone', 'is_active']
    list_filter = ['is_active', 'store']
    search_fields = ['name', 'phone', 'email']


# Configuration Admin pour Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['reference', 'name', 'store', 'unit', 'min_stock_alert', 'is_active']
    list_filter = ['is_active', 'store', 'unit']
    search_fields = ['reference', 'name']
    readonly_fields = ['created_at']


# Configuration Admin pour ProductStock
@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'last_updated']
    list_filter = ['warehouse__store', 'warehouse', 'last_updated']
    search_fields = ['product__reference', 'product__name', 'warehouse__name']
    readonly_fields = ['last_updated']


# Configuration Admin pour Account
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_type', 'store', 'balance', 'is_active']
    list_filter = ['account_type', 'is_active', 'store']
    search_fields = ['name']
    readonly_fields = ['created_at']


# Inline pour les articles des bons d'entrée
class StockEntryItemInline(admin.TabularInline):
    model = StockEntryItem
    extra = 1
    readonly_fields = ['total_price']


# Configuration Admin pour StockEntry
@admin.register(StockEntry)
class StockEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_number', 'supplier', 'warehouse', 'total_amount', 'created_at']
    list_filter = ['warehouse__store', 'warehouse', 'supplier', 'created_at']
    search_fields = ['entry_number', 'supplier__name']
    readonly_fields = ['entry_number', 'total_amount', 'created_at']
    inlines = [StockEntryItemInline]
    date_hierarchy = 'created_at'


# Inline pour les articles des bons de sortie
class StockExitItemInline(admin.TabularInline):
    model = StockExitItem
    extra = 1
    readonly_fields = ['total_price']


# Configuration Admin pour StockExit
@admin.register(StockExit)
class StockExitAdmin(admin.ModelAdmin):
    list_display = ['exit_number', 'get_customer_name', 'warehouse', 'total_amount', 'created_at']
    list_filter = ['warehouse__store', 'warehouse', 'created_at']
    search_fields = ['exit_number', 'customer__name', 'customer_name']
    readonly_fields = ['exit_number', 'total_amount', 'created_at']
    inlines = [StockExitItemInline]
    date_hierarchy = 'created_at'
    
    def get_customer_name(self, obj):
        return obj.customer.name if obj.customer else obj.customer_name
    get_customer_name.short_description = 'Client'


# Configuration Admin pour Invoice
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'get_customer_name', 'total_amount', 'created_at']
    list_filter = ['stock_exit__warehouse__store', 'created_at']
    search_fields = ['invoice_number', 'customer__name', 'customer_name']
    readonly_fields = ['invoice_number', 'total_amount', 'created_at']
    date_hierarchy = 'created_at'
    
    def get_customer_name(self, obj):
        return obj.customer.name if obj.customer else obj.customer_name
    get_customer_name.short_description = 'Client'


# Configuration Admin pour FinancialTransaction
@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_number', 'transaction_type', 'amount', 'from_account', 'to_account', 'created_at']
    list_filter = ['transaction_type', 'from_account__store', 'created_at']
    search_fields = ['transaction_number', 'description']
    readonly_fields = ['transaction_number', 'created_at']
    date_hierarchy = 'created_at'