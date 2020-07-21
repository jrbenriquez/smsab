from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MarketingProfile(models.Model):
    user = models.OneToOneField(User, related_name='marketing_profile', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)

    @classmethod
    def create_profile(cls, first_name, last_name, email):
        user, created = User.objects.get_or_create(
            username=email,
            email=email,
        )

        profile = cls.objects.create(
            user=user,
            first_name=first_name, last_name=last_name)

        return profile


class OperationsProfile(models.Model):
    user = models.OneToOneField(User, related_name='operations_profile', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)

    @classmethod
    def create_profile(cls, first_name, last_name, email):
        user, created = User.objects.get_or_create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        profile = cls.objects.create(
            user=user, first_name=first_name, last_name=last_name)

        return profile

