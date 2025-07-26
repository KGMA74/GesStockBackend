from .serializers import (
    CustomUserSerializer, CreateUserSerializer
)
from django.contrib.auth import login, user_logged_in
from .models import User
from django.conf import settings 
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import api_view, action, permission_classes
from djoser.social.views import ProviderAuthView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .authentication import CustomAuthenticationBackend


# from authentication.permissions import CanApproveLevel1, CanApproveLevel2, CanApproveLevel3
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from .utils import set_auth_cookie
from .models import Store
# Permission
from django.contrib.auth import user_logged_in
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

class StoreContextMixin:
    """
    Mixin pour gérer le contexte store dans les vues.
    Assure que l'utilisateur a un store valide et active.
    """
    
    @property
    def store_id(self):
        """Retourne l'ID du store de l'utilisateur connecté."""
        store = self.store
        return store.id if store else None
    
    @property
    def store(self):
        """Retourne le store de l'utilisateur connecté."""
        if not hasattr(self.request, 'user') or not self.request.user.is_authenticated:
            return None
        return getattr(self.request.user, 'store', None)

    def dispatch(self, request, *args, **kwargs):
        """
        Vérifie que l'utilisateur a un store valide avant de traiter la requête.
        """
        try:
            store = self.store
            if not store:
                logger.warning(f"Tentative d'accès sans store valide par l'utilisateur {request.user.id}")
                return Response(
                    {
                        'error': 'Marchand non autorisé ou non trouvé',
                        'detail': 'Votre compte doit être associé à un marchand valide.'
                    }, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if not store.is_active:
                logger.warning(f"Tentative d'accès avec store inactif {store.id} par l'utilisateur {request.user.id}")
                return Response(
                    {
                        'error': 'Marchand désactivé',
                        'detail': 'Votre marchand est actuellement désactivé.'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du store: {str(e)}")
            return Response(
                {'error': 'Erreur interne du serveur'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_store_queryset(self, queryset):
        """
        Filtre le queryset pour ne retourner que les objets du store actuel.
        """
        store = self.store
        if not store:
            return queryset.none()
            
        # Vérifier si le modèle a un champ store
        if hasattr(queryset.model, 'store'):
            return queryset.filter(store=store)
        
        # Si pas de champ store, retourner le queryset complet
        # (à adapter selon la logique métier)
        return queryset
    

def test(request):
    from django.shortcuts import render
    return render(request, 'accounts/test.html')



class CustomProviderAuthView(ProviderAuthView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201 and response.data:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')
            if access_token:
                set_auth_cookie(response, 'access', access_token, settings.AUTH_COOKIE_ACCESS_MAX_AGE)
            if refresh_token:
                set_auth_cookie(response, 'refresh', refresh_token, settings.AUTH_COOKIE_REFRESH_MAX_AGE)
        return response
    
#customisation de la class TokenObtainPairView pour que les tokens passes par les cookies et non les headers donc plus securise
class CustomTokenObtainPairView(TokenObtainPairView, StoreContextMixin):
    def post(self, request, *args, **kwargs):
        _response = super().post(request, *args, **kwargs)
        response = Response({}, status=status.HTTP_200_OK)
        
        if _response.status_code == 200 and _response.data:
            access_token = _response.data.get('access')
            refresh_token = _response.data.get('refresh')

            if access_token:
                set_auth_cookie(response, 'access', access_token, settings.AUTH_COOKIE_ACCESS_MAX_AGE)
                
            if refresh_token:
                set_auth_cookie(response, 'refresh', refresh_token, settings.AUTH_COOKIE_REFRESH_MAX_AGE)
    
            try:

                user = _response.data.get('user')
                
                # Si l'utilisateur est staff, créer une session Django
                # TODO:  remove this later
                if user.is_staff:
                    login(request, user, backend='api.authentication.CustomAuthenticationBackend')
                else:
                    pass
                    
                user_serializer = CustomUserSerializer(user, context = {'request': request})
                response.data = user_serializer.data
            
            except User.DoesNotExist:
                pass
            
            return response

        return _response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')
        
        if refresh_token:
            mutable_data = request.data.copy()
            mutable_data['refresh'] = refresh_token
            request._full_data = mutable_data
            
            
        _response = super().post(request, *args, **kwargs)
        response = Response(status=status.HTTP_200_OK)
        print(_response)
        if _response.status_code == 200 and _response.data:
            access_token = _response.data.get('access')
            refresh_token = _response.data.get('refresh')
            
            # Update the tokens
            if access_token:
                set_auth_cookie(response, 'access', access_token, settings.AUTH_COOKIE_ACCESS_MAX_AGE)
                
            if refresh_token:
                set_auth_cookie(response, 'refresh', refresh_token, settings.AUTH_COOKIE_REFRESH_MAX_AGE)
            
            return response
        
        return _response

class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        if not request.data.get('token') and request.COOKIES.get('access'):
            data = request.data.copy()
            
            data['token'] = request.COOKIES.get('access')
            request.data = data
            
        return super().post(request, *args, **kwargs)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def LogoutView(request):
    try:
        refresh_token = request.COOKIES.get('refresh')
        response = Response({"detail": "Déconnexion réussie."}, status=status.HTTP_205_RESET_CONTENT)
        
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
        # Supprime les cookies
        set_auth_cookie(response, 'access', '', max_age=0)
        set_auth_cookie(response, 'refresh', '', max_age=0)
        
        request.session.flush()
        return response
            
    except TokenError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": "Une erreur s'est produite lors de la déconnexion"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomUserViewSet(UserViewSet, StoreContextMixin):
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        """Retourne le queryset ordonné des User du store courant."""
        return self.get_store_queryset(User.objects.all().order_by('-created_at', 'fullname'))
    
    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        if self.action == 'create':
            return [IsAuthenticated()] #ajout de permission personnaliser pour lajout
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):        
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                user = serializer.save()

                if user.is_superuser and not request.user.is_superuser:
                    raise ValidationError("You cannot create a superuser.")
        except:
            return Response({"error": "Un utilisateur avec ces identifiants existe deja"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "detail": "Utilisateur créé avec succès",
            "user_id": user.id
        }, status=status.HTTP_201_CREATED)
        
        
    @action(["post"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        from djoser.compat import get_user_email
        from djoser.conf import settings
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()

        if user:
            context = {"user": user, "store_code": user.store.store_code}
            to = [get_user_email(user)]
            settings.EMAIL.password_reset(self.request, context).send(to)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['post'], detail=True, url_path='toggle-activation-status')
    def toggle_activation_status(self, request, id=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        return Response(status=status.HTTP_200_OK)
    
    @action(methods=['post'], detail=True, url_path='grant-permission')
    def grant_permission(self, request, id=None):
        user = self.get_object()
        user.grant_permission(request.data.get('permission_code'), granted_by=request.user)
        return Response(status=status.HTTP_200_OK)
    
    @action(methods=['post'], detail=True, url_path='revoke-permission')
    def revoke_permission(self, request, id=None):
        user = self.get_object()
        user.revoke_permission(request.data.get('permission_code'))
        return Response(status=status.HTTP_200_OK)
    
class testViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer