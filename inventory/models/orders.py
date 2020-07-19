from django.db import models
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey
from smsab.models import TimeStampedModel, UUIDModel
from inventory.models.items import Item, ItemStock
from simple_history.models import HistoricalRecords

User = get_user_model()


class Order(TimeStampedModel, UUIDModel):

    class OrderStatus(models.IntegerChoices):
        NEW = 1
        PENDING = 2
        ASSIGNED = 3
        FOR_DELIVERY = 4
        COMPLETE = 5
        CANCELLED = 6

    status = models.IntegerField(choices=OrderStatus.choices, default=OrderStatus.NEW)
    history = HistoricalRecords()

    def cancel(self, user):
        cancellation = CancelOrder.objects.create(
            order=self,
            user=user)
        self.status = self.OrderStatus.CANCELLED
        self.save(update_fields=['status'])

    @property
    def stock(self):
        return self.stocks.get().stock

    @property
    def quantity(self):
        return self.stocks.get().quantity

    @property
    def variations(self):
        params_list = self.order_forms.get().parameter_list
        return params_list

    @property
    def buyer(self):
        order_form = self.order_forms.last()
        if order_form:
            return order_form.customer
        else:
            return None


class CancelOrder(TimeStampedModel):
    order = models.OneToOneField(Order, related_name='cancellation', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='orders_cancelled', on_delete=models.CASCADE)


class OrderAssignment(TimeStampedModel):
    order = models.ForeignKey(Order, related_name='assignments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='orders_assigned', on_delete=models.CASCADE)


class ItemOrder(TimeStampedModel):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name='orders',
                             null=True, blank=True,
                             on_delete=models.CASCADE,
                             )


class StockOrder(TimeStampedModel):
    order = models.ForeignKey(Order, related_name='stocks', on_delete=models.CASCADE)
    stock = models.ForeignKey(ItemStock, related_name="stock_orders", on_delete=models.CASCADE, null=True)
    quantity = models.DecimalField(max_digits=11, decimal_places=2, default=0)


class OrderNotes(MPTTModel, TimeStampedModel):
    user = models.ForeignKey(User, related_name='order_notes', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='notes', on_delete=models.CASCADE)
    text = models.CharField(max_length=512)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['created_at']
