from rest_framework.request import Request
from .models import User, Store
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
class CustomJWTAuthentication(JWTAuthentication):
    """
        Ici on fait juste une surcharge de la fonction authenticate de JWTAuthentication pour recuperer les tokens( access token) 
        a partir du access cookie si present(pour des raisons de securité_), 
        A defaut de la presence du access token a partir du headers de la requete  
    """
    def authenticate(self, request: Request):
        try:
            header = self.get_header(request)
            raw_token = self.get_raw_token(header) if header else request.COOKIES.get(settings.AUTH_COOKIE)

            if raw_token is None:
                return None

            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except Exception as e:
            logger.warning(f"Authentication failed: {e}")
            return None
        
class CustomAuthenticationBackend(ModelBackend):
   def authenticate(self, request, username=None, password=None, store_name=None, **kwargs):
        user = None
        
        # Cas global : utilisateur du support (superuser sans store)
        if not store_name:
            try:
                print("-----------------",username)
                
                user = User.objects.get(
                    username=username,
                    store__isnull=True
                )
                print(User.objects.get(username=username)==None)
            except User.DoesNotExist:
                print("ddd")
                return None
        else:
            try:
                store = Store.objects.get(name=store_name)
                print(store)
                if not store.is_active:
                    return None
            except Store.DoesNotExist:
                return None
            try:
                user = User.objects.get(
                    username=username,
                    store=store
                )
                print(user)
            except User.DoesNotExist:
                return None

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
