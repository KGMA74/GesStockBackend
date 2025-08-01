from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView, CustomTokenRefreshView, CustomTokenVerifyView, 
    CustomUserViewSet,
    LogoutView, testViewSet,
    ProductViewSet, StockEntryViewSet, StockExitViewSet,
    CustomerViewSet, SupplierViewSet, WarehouseViewSet, AccountViewSet, InvoiceViewSet,
    FinancialTransactionViewSet,
    stock_stats
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'stock-entries', StockEntryViewSet, basename='stock-entry')
router.register(r'stock-exits', StockExitViewSet, basename='stock-exit')
router.register(r'financial-transactions', FinancialTransactionViewSet, basename='financial-transaction')



urlpatterns = [
    path('jwt/create/', CustomTokenObtainPairView.as_view()),
    path('jwt/refresh/', CustomTokenRefreshView.as_view()),
    path('jwt/verify/', CustomTokenVerifyView.as_view()),
    path('logout/', LogoutView),
    path('stock-stats/', stock_stats, name='stock-stats'),
    path('', include(router.urls)),
    
    # path('test/', test )
    # path('test/', testViewSet.as_view({'get': 'list'})),
]
