from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import PermissionsMixin

from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=200, null=True, unique=True)
    email = models.EmailField(null=True, unique=True, max_length=255)
    first_name = models.CharField(null=True, max_length=255)
    last_name = models.CharField(null=True, max_length=255)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    google_access_token = models.TextField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @classmethod
    def create_user(cls, first_name, last_name, email):
        user, created = cls.objects.get_or_create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        return user

    @property
    def is_marketing(self):
        if hasattr(self, 'marketing_profile'):
            return True
        return False

    @property
    def is_operations(self):
        if hasattr(self, 'operations_profile'):
            return True
        return False

