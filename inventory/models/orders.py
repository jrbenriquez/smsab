from django.db import models
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey
from inventory.models.core import TimeStampedModel, UUIDModel
from inventory.models.items import Item
from simple_history.models import HistoricalRecords

User = get_user_model()


class Order(TimeStampedModel, UUIDModel):

    class OrderStatus(models.IntegerChoices):
        NEW = 1
        PENDING = 2
        ASSIGNED = 3
        FOR_DELIVERY = 4
        COMPLETE = 5

    status = models.IntegerField(choices=OrderStatus.choices)
    history = HistoricalRecords()


class ItemOrder(TimeStampedModel):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name='events',
                             null=True, blank=True,
                             on_delete=models.CASCADE,
                             )
    quantity = models.DecimalField(max_digits=11, decimal_places=2, default=0)


class OrderNotes(MPTTModel, TimeStampedModel):
    user = models.ForeignKey(User, related_name='order_notes', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='notes', on_delete=models.CASCADE)
    text = models.CharField(max_length=512)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['created_at']
