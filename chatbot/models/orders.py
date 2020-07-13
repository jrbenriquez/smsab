from django.db import models


class MessengerOrderForm(models.Model):
    class FormStatus(models.IntegerChoices):
        OPEN = 1
        CONFIRMED = 2
        EXPIRED = 3
        CANCELLED = 4

    status = models.IntegerField(choices=FormStatus.choices, default=FormStatus.OPEN)

    item_id = models.CharField(max_length=16)
    parameters = models.TextField()
    contact_details = models.TextField()
    provided_name = models.TextField()
    address = models.TextField()

    def add_parameters(self, name, value):
        pass

    def get_parameters(self):
        pass
