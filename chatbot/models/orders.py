from django.db import models
from chatbot.models.users import MessengerProfile
from smsab.models import TimeStampedModel
from inventory.models.items import Item, ItemStock


class MessengerOrderForm(TimeStampedModel):
    class FormStatus(models.IntegerChoices):
        OPEN = 1
        CONFIRMED = 2
        EXPIRED = 3
        CANCELLED = 4

    status = models.IntegerField(choices=FormStatus.choices, default=FormStatus.OPEN)

    customer = models.ForeignKey(MessengerProfile, related_name="messenger_forms", on_delete=models.CASCADE)

    item = models.ForeignKey(Item, related_name="item_forms", on_delete=models.CASCADE, null=True)
    stock = models.ForeignKey(ItemStock, related_name="stock_forms", on_delete=models.CASCADE, null=True)
    parameters = models.TextField(null=True)
    contact_details = models.TextField(null=True)
    provided_name = models.TextField(null=True)
    address = models.TextField(null=True)

    def add_parameters(self, name, value):
        pass

    def get_parameters(self):
        pass
