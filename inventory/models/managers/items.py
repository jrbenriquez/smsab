from django.db import models


class ItemQueryset(models.QuerySet):
    def featured(self):
        return self.filter(featured=True)


ItemManager = ItemQueryset.as_manager()
