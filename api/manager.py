from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, store=None, **extra_fields):
        if not username:
            raise ValueError("Le champ 'username' est requis.")

        # Si ce n'est pas un superuser, store est obligatoire
        if not extra_fields.get('is_superuser') and store is None:
            raise ValidationError("Le champ 'store' est obligatoire sauf pour les superusers (support technique).")

        user = self.model(
            username=username,
            store=store,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # On laisse store=None pour le support technique global
        return self.create_user(username=username, password=password, store=None, **extra_fields)
