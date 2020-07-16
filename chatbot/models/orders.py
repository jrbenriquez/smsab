from django.db import models
from chatbot.models.users import MessengerProfile
from smsab.models import TimeStampedModel
from inventory.models.items import Item, ItemStock
from inventory.models.orders import Order


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
    order = models.ForeignKey(Order, related_name='order_forms', on_delete=models.CASCADE, null=True)
    parameters = models.TextField(null=True)
    contact_details = models.TextField(null=True)
    provided_name = models.TextField(null=True)
    address = models.TextField(null=True)

    @property
    def parameter_list(self):
        current_params = self.parameters
        if not current_params:
            current_params = ""
        params_list = current_params.split("|")
        return params_list

    @property
    def parameter_dict(self):
        params_list = self.parameter_list
        params_dict = {}
        for param in params_list:
            if not param:
                continue
            split_param = param.split(':')
            parameter_name = split_param[0]
            parameter_value = split_param[1]
            params_dict[parameter_name] = parameter_value
        return params_dict

    @property
    def missing_parameters(self):
        available_params = self.item.get_params
        params_dict = self.parameter_dict.keys()
        return available_params.difference(params_dict)


    def set_parameters(self, name, value):
        params_dict = self.parameter_dict
        params_dict[name] = value
        joined_params_list = []
        for param in params_dict:
            join_param = ":".join([param, params_dict[param]])
            joined_params_list.append(join_param)

        final_params = '|'.join(joined_params_list)

        self.parameters = final_params
        self.save(update_fields=['parameters'])

