
from pathlib import Path
from os import getenv, path
import dj_database_url
import dotenv
from datetime import timedelta
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_file = BASE_DIR / '.env.local'

if path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv('DJANGO_SECRET_KEY', get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv('DEBUG', 'False') == 'True'

import logging
logger = logging.getLogger(__name__)
logger.warning(f'DEBUG mode is {"on" if DEBUG else "off"}')

INSTALLED_APPS = [
    # 'daphne',
    # "unfold",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt.token_blacklist',
    
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'djoser',

    
    # project applications
    'api',

]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'GesStockBackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'GesStockBackend.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]


STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTHENTICATION_BACKENDS = [
    'api.authentication.CustomAuthenticationBackend',
]


REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.authentication.CustomJWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 4,
}

DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': 'auth/password-reset/{uid}/{token}?mc={store_code}',
    'SEND_ACTIVATION_EMAIL': True,
    'ACTIVATION_URL': 'activation/{uid}/{token}',
    'USER_CREATE_PASSWORD_RETYPE': False,  
    'PASSWORD_RESET_CONFIRM_RETYPE': True,
    'TOKEN_MODEL': None,  
    "EMAIL": {
        # "activation": "accounts.emails.CustomActivationEmail",
    },
    'PERMISSIONS': {
        'user':  ["rest_framework.permissions.IsAuthenticated"],
        'user_list':  ["rest_framework.permissions.IsAuthenticated"]
    },
    'SERIALIZERS': {
        'user': 'api.serializers.CustomUserSerializer',
        'current_user': 'api.serializers.CustomUserSerializer',
        # 'password_reset': 'api.serializers.CustomPasswordResetSerializer',
    }
}


SIMPLE_JWT = {
    # Durée de vie des tokens d'accès et de rafraîchissement
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    # Gestion des tokens de rafraîchissement
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    # Mise à jour du dernier login
    "UPDATE_LAST_LOGIN": True,

    # Clés et algorithmes
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,  # Clé secrète pour signer les tokens
    "VERIFYING_KEY": "",  # Clé publique pour vérifier les tokens si nécessaire

    # Autres paramètres de validation
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,  # Tolérance pour la validation des dates

    # En-têtes d'authentification
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",

    # Configuration de l'utilisateur
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    # Classes et claims des tokens
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",

    # Configuration des tokens de type "sliding"
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=10),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    # Sérialiseurs pour les opérations sur les tokens
    "TOKEN_OBTAIN_SERIALIZER": "api.serializers.CustomTokenObtainPairSerializer", # Custom
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}


if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    CSRF_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True

DATABASES = {
    'default': dj_database_url.config(
        default=getenv("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=getenv("DATABASE_URL"),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    


AUTH_USER_MODEL = 'api.User'

SITE_NAME = 'gesStock'
DOMAIN = getenv('FRONTEND_DOMAIN') # domaine qui sera specifie dans les mails d'acitvation, de reset de mot de passe .. 

CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
CORS_ALLOWED_ORIGINS = getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CSRF_TRUSTED_ORIGINS = getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:3000').split(',')
logger.warning(CORS_ALLOWED_ORIGINS)

#cookies d'authentifications
AUTH_COOKIE = 'access'
AUTH_COOKIE_ACCESS_MAX_AGE = int(timedelta(minutes=500).total_seconds())
AUTH_COOKIE_REFRESH_MAX_AGE = int(timedelta(days=1).total_seconds())
AUTH_COOKIE_SECURE = getenv('AUTH_COOKIE_SECURE', f'{not DEBUG}') == 'True'
AUTH_COOKIE_HTTP_ONLY = True
AUTH_COOKIE_PATH = '/'
AUTH_COOKIE_SAMESITE = getenv('AUTH_COOKIE_SAMESITE', 'Lax')
AUTH_COOKIE_DOMAIN = getenv('AUTH_COOKIE_DOMAIN', 'localhost')
