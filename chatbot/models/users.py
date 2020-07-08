from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class MessengerProfile(models.Model):

    user_id = models.CharField(max_length=256, unique=True)
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)
    contact_details = models.CharField(max_length=256, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    last_active = models.DateTimeField(null=True, blank=True)
    joined = models.DateTimeField(auto_now_add=True)