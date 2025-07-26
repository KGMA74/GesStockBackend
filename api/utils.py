from django.conf import settings

def set_auth_cookie(response, key, value, max_age):
    response.set_cookie(
        key,
        value,
        max_age,
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        path=settings.AUTH_COOKIE_PATH,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        domain=settings.AUTH_COOKIE_DOMAIN
    )