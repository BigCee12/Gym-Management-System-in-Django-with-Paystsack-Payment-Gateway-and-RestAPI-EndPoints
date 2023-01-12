# Create your models here.
from django.contrib.auth.base_user import BaseUserManager

from django.contrib.auth.hashers import make_password


class CustomClientManager(BaseUserManager):
    def create_user(self, email, password=None, **extrafields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extrafields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extrafields):
        user = self.create_user(email, password, *extrafields)
        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user
