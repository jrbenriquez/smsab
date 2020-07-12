from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class MessengerProfile(models.Model):

    user_id = models.CharField(max_length=256, unique=True)
    page_id = models.CharField(max_length=256, null=True, blank=True)
    status = models.CharField(max_length=32, null=True, blank=True)
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    gender = models.CharField(max_length=16, null=True, blank=True)
    profile_pic = models.CharField(max_length=256, null=True, blank=True)
    live_chat_url = models.CharField(max_length=256, null=True, blank=True)
    phone = models.CharField(max_length=32, null=True, blank=True)

    address = models.CharField(max_length=256, null=True, blank=True)
    contact_details = models.CharField(max_length=256, null=True, blank=True)
    provided_name = models.CharField(max_length=128, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    last_interaction = models.DateTimeField(null=True, blank=True)
    joined = models.DateTimeField(auto_now_add=True)