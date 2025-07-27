from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, store=None, **extra_fields):
        if not username:
            raise ValueError("Le champ 'username' est requis.")

        if not extra_fields.get('is_superuser') and store is None:
            raise ValidationError("Le champ 'store' est obligatoire sauf pour les superusers (support technique).")

        email = self.normalize_email(email)

        user = self.model(
            username=username,
            email=email,
            store=store,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username=username, email=self.normalize_email(email), password=password, store=None, **extra_fields)
