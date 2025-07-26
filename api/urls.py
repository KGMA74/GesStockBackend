from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView, CustomTokenRefreshView, CustomTokenVerifyView, 
    CustomUserViewSet,
    LogoutView, testViewSet
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')



urlpatterns = [
    path('jwt/create/', CustomTokenObtainPairView.as_view()),
    path('jwt/refresh/', CustomTokenRefreshView.as_view()),
    path('jwt/verify/', CustomTokenVerifyView.as_view()),
    path('logout/', LogoutView),
    path('', include(router.urls)),
    
    # path('test/', test )
    # path('test/', testViewSet.as_view({'get': 'list'})),
]
