from django.db import models
from smsab.models import UUIDModel, TimeStampedModel
from mptt.models import MPTTModel, TreeForeignKey


class Location(MPTTModel, UUIDModel, TimeStampedModel):
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=128, null=True, blank=True)
    address = models.CharField(max_length=128, null=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.get_full_name

    @property
    def get_full_name(self):
        full_name = self.name
        parents = self.get_ancestors()
        if parents:
            for parent in parents:
                full_name = parent.name + '/' + full_name

        return full_name

    class MPTTMeta:
        order_insertion_by = ['name']
