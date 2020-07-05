import itertools
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from inventory.utils.uploaders import upload_item_photo
from .core import UUIDModel, TimeStampedModel
from .categories import Category
from .locations import Location
from .managers.items import ItemManager


class Item(MPTTModel, UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=256, unique=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    category = TreeForeignKey(Category, related_name='items',
                              null=True, blank=True,
                              on_delete=models.DO_NOTHING,
                              help_text=_('Item category'))
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    objects = ItemManager

    # TODO Create a separate FeaturedItem and FeaturedEvent for this field
    featured = models.BooleanField(default=False)

    def set_featured(self, state=True):
        self.featured = state
        self.save(update_fields=['featured'])

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return "{} - {} - {}".format(self.id, self.name, self.price)

    @property
    def get_quantity(self):
        stock_count = self.stocks.all().aggregate(total=Sum('quantity'))['total']
        return stock_count

    @property
    def get_photo(self):
        obj = self.photos.last()
        return obj.photo.url

    @property
    def get_variation_count(self):
        variation_count = self.stocks.count()
        return variation_count

    def create_item_stocks(self,
                    serializer, price, quantity,
                    category_id, location_id,
                    parameter_data):

        def _perform_create(_item, _price, _location_id, _quantity):
            stock_serializer = serializer(data=
            {
                "item": self.pk,
                "price": price,
                "location": location_id,
                "quantity": quantity
            }
            )
            stock_serializer.is_valid(raise_exception=True)
            stock = stock_serializer.save()
            return stock

        if not parameter_data:
            # Create 1 Item Stock
            stock = _perform_create(self, price, location_id, quantity)

        else:
            # Create Stocks for all variations
            variations = list(itertools.product(*parameter_data))
            for variation in variations:
                stock = _perform_create(self, price, location_id, quantity)
                for param in variation:
                    param_template_id = list(param.items())[0][0]
                    param_value = list(param.items())[0][1]
                    param_template = ParameterTemplate.objects.get(id=param_template_id)
                    parameter, created = Parameter.objects.get_or_create(name=param_template.name,
                                                         value=param_value,
                                                         )
                    # Create Relation
                    param_relation, created = ParameterItemRelation.objects.get_or_create(
                        stock=stock, parameter=parameter)

        return self.stocks.all()


class ItemStock(MPTTModel, UUIDModel, TimeStampedModel):
    item = models.ForeignKey(Item, related_name='stocks', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    location = models.ForeignKey('inventory.Location', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['price']


class ItemPhoto(TimeStampedModel):

    item = models.ForeignKey(Item, related_name='photos', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=upload_item_photo)


class ParameterTemplate(models.Model):
    class ParameterType(models.TextChoices):
        STRING = 'S'
        INTEGER = 'I'
        DECIMAL = 'D'

    DEFAULT_TEMPLATES = {
        'Size': ParameterType.STRING,
        'Color': ParameterType.STRING
    }

    name = models.CharField(max_length=64, null=True, blank=True, unique=True)
    parameter_type = models.CharField(max_length=8, choices=ParameterType.choices)

    def __str__(self):
        return f"{self.name} - {self.pk}"

    @classmethod
    def initialize_parameter_templates(cls):
        for name in cls.DEFAULT_TEMPLATES:
            obj, created = cls.objects.get_or_create(name=name)

        return True


class Parameter(TimeStampedModel):
    name = models.CharField(max_length=64)
    value = models.CharField(max_length=64)

    class Meta:
        unique_together = [['name', 'value']]


class ParameterItemRelation(TimeStampedModel):
    stock = models.ForeignKey(ItemStock, related_name='parameters',
                             null=True, blank=True,
                             on_delete=models.CASCADE,
                             )
    parameter = models.ForeignKey(Parameter, related_name='items',
                             null=True, blank=True,
                             on_delete=models.CASCADE,
                             )

    class Meta:
        unique_together = [['stock', 'parameter']]
