from django.db import models
from inventory.models.core import TimeStampedModel
from inventory.models.items import Item
from inventory.utils.uploaders import upload_event_photo


class Event(TimeStampedModel):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=256, null=True, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    link = models.CharField(max_length=512, null=True, blank=True)

    @property
    def get_photo(self):
        obj = self.photos.last()
        if not obj:
            return 'https://placeimg.com/480/480/tech'
        return obj.photo.url


class EventPhoto(TimeStampedModel):
    event = models.ForeignKey(Event, related_name='photos', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=upload_event_photo)


class EventItemRelation(TimeStampedModel):
    item = models.ForeignKey(Item, related_name='events_featured',
                              null=True, blank=True,
                              on_delete=models.CASCADE,
                              )
    event = models.ForeignKey(Event, related_name='items_featured',
                              null=True, blank=True,
                              on_delete=models.CASCADE,
                              )

    class Meta:
        unique_together = [['item', 'event']]

