import re

from functools import reduce
from urllib import parse

from django.conf import settings

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from api.serializers.messenger_order import MessengerOrderFormSerializer
from api.serializers.orders import OrderSerializer

from chatbot.models.users import MessengerProfile
from chatbot.models.orders import MessengerOrderForm
from chatbot.permissions.manychat import ManyChatAppEntryPermission, ManyChatAppGETPermission, ManyChatAppPOSTPermission
from chatbot.serializers.users import MessengerProfileSerializer
from chatbot.responses.manychat.response import response_template
from chatbot.responses.manychat.messages import (add_message_text, add_message_card, create_card_data,
                                                 add_button_to_element, add_message_gallery, add_action_to_element,
                                                 add_message_image, add_quick_reply_to_element)

from inventory.models.events import Event
from inventory.models.items import Item, ParameterItemRelation
from inventory.models.orders import Order, ItemOrder, StockOrder


ORDER_FLOW = 'content20200610094539_642137'
VIEW_CATALOG_FLOW = 'content20200702123449_857707'
LOAD_MORE = 'content20200712104006_431864'
ITEM_ORDER_FLOW = 'content20200712140119_187521'
CHOOSE_PARAMETERS_FLOW = 'content20200714073931_533653'


def alphanum_sort(l):
    """https://stackoverflow.com/questions/2669059/how-to-sort-alpha-numeric-set-in-python"""
    """ Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


class EntryPointViewSet(ModelViewSet):
    queryset = MessengerProfile.objects.all()
    serializer_class = MessengerProfileSerializer
    permission_classes = [ManyChatAppEntryPermission]
    http_method_names = ['post']

    @action(methods=['post'], detail=True,
            url_path='welcome', url_name='welcome', permission_classes=[ManyChatAppEntryPermission],
            authentication_classes=[])
    def welcome(self, request, pk=None):
        profile = MessengerProfile(user_id=pk)
        events = Event.objects.all()
        active_events = [event for event in events if event.is_active]
        response_data = response_template()

        if active_events:
            gallery_list = []

            for event in active_events:
                event_element = create_card_data(
                    title=event.name,
                    subtitle=f"{event.description} \n {event.start_date.strftime('%B %d %-I:%M %P')} - {event.end_date.strftime('%B %d %-I:%M %P')}",
                    image_url=f"{event.get_photo}"
                )
                if event.link:
                    event_element = add_button_to_element(
                        event_element,
                        button_type="url",
                        caption=f"Go to LiveStream",
                        url=f"{event.link}"
                    )
                event_element = add_button_to_element(
                    event_element,
                    button_type="flow",
                    caption="Shop Now",
                    target=VIEW_CATALOG_FLOW
                )
                gallery_list.append(event_element)

            response_data = add_message_gallery(response_data, gallery_list)
        else:
            response_data = add_message_text(response_data, "Currently, we have no live events.")

            button_data = [
                {
                    "type": "url",
                    "caption": "Go to Page",
                    "url": "https://www.google.com"
                 }
            ]

            response_data = add_message_text(
                response_data,
                "But don't worry! You can still check out our products by visiting our page.",
                button_data=button_data)
        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True,
            url_path='live-catalog', url_name='live-catalog', permission_classes=[ManyChatAppEntryPermission],
            authentication_classes=[])
    def live_catalog(self, request, pk=None):
        profile = MessengerProfile(user_id=pk)

        def _get_active_events():
            events = Event.objects.all()
            active_events = [event for event in events if event.is_active]
            return active_events

        def _get_items_to_show():

            active_events = _get_active_events()

            if active_events:
                _active_items = Item.objects.none()

                for event in active_events:
                    item_relation = event.items_featured.all()
                    event_items = Item.objects.filter(
                        events_featured__in=item_relation,
                        stocks__quantity__gt=0
                    ).order_by('id').distinct()

                    _active_items = _active_items | event_items
                    return _active_items
            else:
                return None

        data = request.data
        active_items = _get_items_to_show()
        custom_fields = data.get('custom_fields')
        last_product = None
        last_browsed_item = None
        gallery_list = []

        if custom_fields:
            last_browsed_item = custom_fields.get('last_browsed_item')

        if last_browsed_item:
            last_product = Item.objects.get(id=last_browsed_item)

        response_data = response_template()

        if active_items:
            active_items = active_items.order_by('id')
            if last_product:
                current_items = active_items.filter(id__gt=last_product.id)[:10]
            else:
                current_items = active_items[:10]
            for item in current_items:
                item_element = create_card_data(
                    title=item.name,
                    subtitle=f"₱ {item.price:,.2f} - {item.description}",
                    image_url=f"{item.get_photo}"
                )
                action_data = [
                    {
                        "action": "set_field_value",
                        "field_name": "item_order_id",
                        "value": f"{item.id}"
                    }
                ]

                item_element = add_button_to_element(
                    item_element,
                    button_type="flow",
                    caption="Get This",
                    target=ITEM_ORDER_FLOW,
                    action_data=action_data
                )

                gallery_list.append(item_element)

        if gallery_list:
            response_data = add_message_gallery(response_data, gallery_list)
            first_product = current_items[0]
            last_product = current_items[len(current_items) - 1]
            previous_products = active_items.filter(id__lt=first_product.id).count()
            if len(current_items) < 10 and not last_browsed_item:
                current_index = len(current_items)
            else:
                current_index = len(current_items) + previous_products
            current_browsing_message = f"Showing {current_index} of {active_items.count()} items"

            if current_index < active_items.count():

                load_more_button = {
                    "type": "flow",
                    "caption": "Load More",
                    "target": LOAD_MORE
                }

                button_data = [load_more_button, ]
            else:
                button_data = []

            response_data = add_message_text(
                response_data,
                current_browsing_message,
                button_data=button_data)

            action_data = {
                "field_name": "last_browsed_item",
                "value": f"{last_product.id}"
            }
            content = response_data.copy()['content']
            content = add_action_to_element(content, action="set_field_value", **action_data)
            response_data['content'] = content
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = add_message_text(response_data, "Currently, we have no live events.")

            button_data = [
                {
                    "type": "url",
                    "caption": "Go to Page",
                    "url": "https://www.google.com"
                }
            ]

            response_data = add_message_text(
                response_data,
                "But don't worry! You can still check out our products by visiting our page.",
                button_data=button_data)
            return Response(response_data, status=status.HTTP_200_OK)


class MessengerOrderViewSet(ModelViewSet):
    queryset = MessengerProfile.objects.all()
    serializer_class = MessengerProfileSerializer
    permission_classes = [ManyChatAppPOSTPermission]
    http_method_names = ['post', 'get']

    @action(methods=['post'], detail=True,
            url_path='start-order', url_name='start-order', permission_classes=[ManyChatAppPOSTPermission],
            authentication_classes=[])
    def start_order(self, request, pk=None):
        profile = MessengerProfile.objects.get(user_id=pk)
        data = request.data

        custom_fields = data.get('custom_fields')
        item_order_id = None
        if custom_fields:
            item_order_id = custom_fields.get('item_order_id')
        item_exists = Item.objects.filter(id=item_order_id)
        if not item_order_id or not item_exists:
            # Got Lost go back prompt
            raise Exception('MISSING PARAMs')

        item = item_exists.get()

        # Create a MessengerOrder Form
        form_data = {
            "item": item_order_id,
            "customer": profile.id
        }

        previous_forms = MessengerOrderForm.objects.filter(customer=profile, status=MessengerOrderForm.FormStatus.OPEN)
        previous_forms.delete()

        serializer = MessengerOrderFormSerializer(data=form_data)
        serializer.is_valid(raise_exception=True)
        order_form = serializer.save()

        variation_reference = {}

        # Create reply showing item details
        response_data = response_template()

        response_data = add_message_text(response_data, f"You are ordering: {item.name}")
        response_data = add_message_image(response_data, item.get_photo)
        response_data = add_message_text(response_data, f"₱ {item.price:,.2f}")

        variations = item.get_params

        button_data = []

        for variation in variations:

            relations = ParameterItemRelation.objects.filter(
                item=item,
                parameter__name=variation,
                stock__quantity__gt=0
            )
            variation_options_available = list(set([x.parameter.value for x in relations]))
            variation_options_available = alphanum_sort(variation_options_available)
            variation_reference[variation] = variation_options_available
            message = f"{variation} available: {','.join(variation_options_available)}"
            response_data = add_message_text(response_data, message)
            button = {
                    "type": "flow",
                    "caption": f"Choose {variation} ",
                    "target": CHOOSE_PARAMETERS_FLOW
                }

            # Add action to set parameter_selection
            button_action_data = {
                "action": "set_field_value",
                "field_name": "parameter_selection",
                "value": f"{variation}"
            }
            button = add_action_to_element(button, **button_action_data)
            button_data.append(button)

        if item.get_variation_count and 0 < item.stocks.all().count() <= 1:
            button = {
                        "type": "flow",
                        "caption": "Order now!",
                        "target": ORDER_FLOW
                    }
            # Set fields for order form
            order_form.stock = item.stocks.last()
            order_form.save(update_fields=["stock"])

            response_data = add_message_text(response_data, "What are you waiting for?", button_data=[button, ])
        else:
            response_data = add_message_text(response_data, "Select Action:", button_data=button_data)

        action_data = {
            "action": "set_field_value",
            "field_name": "open_order_id",
            "value": f"{order_form.id}"
        }
        content = response_data.copy()['content']
        content = add_action_to_element(content, **action_data)
        response_data['content'] = content

        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True,
            url_path='parameter-selection', url_name='parameter-selection', permission_classes=[ManyChatAppPOSTPermission],
            authentication_classes=[])
    def parameter_selection(self, request, pk=None):
        profile = MessengerProfile.objects.get(user_id=pk)
        data = request.data

        custom_fields = data.get('custom_fields')

        if not custom_fields:
            raise Exception('MISSING Custom Fields')
        else:
            item_order_id = custom_fields.get('item_order_id')
            open_order_id = custom_fields.get('open_order_id')
            parameter_selection = custom_fields.get('parameter_selection')

        item_exists = Item.objects.filter(id=item_order_id)
        order_form = MessengerOrderForm.objects.filter(
            id=open_order_id
        )
        if (not item_order_id or not item_exists or
                not open_order_id or
                not parameter_selection or not order_form):

            raise Exception('MISSING PARAMs')
        item = item_exists.get()
        order_form = order_form.get()
        # Check for set_parameter in data
        set_parameter = data.get('set_parameter')
        if set_parameter:
            set_parameter = set_parameter.split(':')

            parameter_name = set_parameter[0]
            parameter_value = set_parameter[1]
            order_form.set_parameters(parameter_name, parameter_value)

            # Get missing parameters
            missing_parameter = list(order_form.missing_parameters)
            if not missing_parameter:
                # proceed_to_order_flow
                final_params = order_form.parameter_list

                param_string = ", ".join(final_params)

                message = f"You chose {param_string}"
                response_data = response_template()

                button = {
                    "type": "flow",
                    "caption": "Proceed with Order",
                    "target": ORDER_FLOW
                }
                catalog_button = {
                    "type": "flow",
                    "caption": "Back to Catalog",
                    "target": VIEW_CATALOG_FLOW
                }

                response_data = add_message_text(response_data, message, button_data=[catalog_button, button])
                return Response(response_data, status=status.HTTP_200_OK)



            else:
                missing_parameter = missing_parameter[0]
                parameter_selection = missing_parameter


        # Get all available options for the parameter in parameter_selection:
        response_data = response_template()
        button = {
            "type": "flow",
            "caption": "Back to Item",
            "target": ITEM_ORDER_FLOW
        }
        response_data = add_message_text(
            response_data,
            f"What {parameter_selection} do you want?",
            button_data=[button])


        relation_values = alphanum_sort(item.variations_available(parameter_selection, previous_selections=order_form.parameter_dict))
        for value in relation_values:
            headers = {
                "X-App-Id": "smsab"
            }

            url_list = [
                settings.PUBLIC_PATH,
                settings.CHATBOT_HASH,
                reverse('chatbot:order-parameter-selection', kwargs={"pk": pk})
            ]

            set_value_url = reduce(lambda a, b: parse.urljoin(a, b), url_list)

            payload = data
            payload["set_parameter"] = f'{parameter_selection}:{value}'
            content = response_data.copy()['content']

            content = add_quick_reply_to_element(
                content, qtype="dynamic_block_callback",
                caption=value, url=set_value_url,
                method='post', headers=headers, payload=payload
                )
            print(content)
            response_data['content'] = content

        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True,
            url_path='form-summary', url_name='form-summary',
            permission_classes=[ManyChatAppPOSTPermission],
            authentication_classes=[])
    def form_summary(self, request, pk=None):
        profile = MessengerProfile.objects.get(user_id=pk)
        data = request.data
        # Create Form summary to be display to the user to confirm or cancel order
        response_data = response_template()

        response_data = add_message_text(response_data, "Thanks! 👍")
        response_data = add_message_text(response_data, "Here's a summary of your order:")

        custom_fields = data.get('custom_fields')

        if not custom_fields:
            raise Exception('MISSING Custom Fields')

        # Get the custom fields we need to set
        fields_to_get = ['name', 'contact', 'address', 'open_order_id']
        order_data = {}
        for field in fields_to_get:
            value = custom_fields.get(field)
            if not value:
                raise Exception(f"Missing {field}")
            order_data[field] = value
        profile.provided_name = order_data.get('name')
        profile.contact_details = order_data.get('contact')
        profile.address = order_data.get('address')

        profile.save(update_fields=['provided_name', 'contact_details', 'address'])

        messenger_order = MessengerOrderForm.objects.get(id=order_data['open_order_id'])
        item = messenger_order.item
        if not messenger_order.stock:
            params_dict = messenger_order.parameter_dict
            stocks = item.stocks.all()

            for param_name in params_dict:
                stocks = stocks.filter(
                    parameters__parameter__name=param_name,
                    parameters__parameter__value=params_dict[param_name]
                )

            stock = stocks.distinct().get()

        else:
            stock = messenger_order.stock

        response_data = add_message_image(response_data, stock.get_photo)

        item_details = f"Order Details: \n\n" \
                        f"{stock.item.name} \n" \
                        f"{order_data['name']} \n" \
                        f"{order_data['address']} \n" \
                        f"{order_data['contact']}\n\n" \
                        f"Total Amount: ₱ {stock.price:,.2f}"

        for param in stock.parameter_list:
            item_details += '\n'
            for p in param:
                item_details += f'{p} '

        response_data = add_message_text(response_data, item_details)

        cancel_order_button = {
                    "type": "flow",
                    "caption": "Cancel Order",
                    "target": VIEW_CATALOG_FLOW
                }

        confirm_order_button = {
                    "type": "node",
                    "caption": "Confirm Order",
                    "target": "Confirm Order"
                }

        message = "Please confirm to continue with your order"

        response_data = add_message_text(response_data, message, button_data=[cancel_order_button, confirm_order_button])

        return Response(response_data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True,
            url_path='confirm-order', url_name='confirm-order',
            permission_classes=[ManyChatAppPOSTPermission],
            authentication_classes=[])
    def confirm_order(self, request, pk=None):
        profile = MessengerProfile.objects.get(user_id=pk)
        data = request.data

        custom_fields = data.get('custom_fields')

        if not custom_fields:
            raise Exception('MISSING Custom Fields')

        # Get the custom fields we need to set
        fields_to_get = ['name', 'contact', 'address', 'open_order_id']
        order_data = {}
        for field in fields_to_get:
            value = custom_fields.get(field)
            if not value:
                raise Exception(f"Missing {field}")
            order_data[field] = value

        profile.provided_name = order_data.get('name')
        profile.contact_details = order_data.get('contact')
        profile.address = order_data.get('address')

        profile.save(update_fields=['provided_name', 'contact_details', 'address'])

        messenger_order = MessengerOrderForm.objects.get(id=order_data['open_order_id'])

        messenger_order.provided_name = order_data.get('name')
        messenger_order.contact_details = order_data.get('contact')
        messenger_order.address = order_data.get('address')

        messenger_order.save(update_fields=['provided_name', 'contact_details', 'address'])
        # Create Order here

        serializer = OrderSerializer(data={
            "status": Order.OrderStatus.NEW
        })
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        # Assign Item and Stock here
        item = messenger_order.item
        if not messenger_order.stock:
            params_dict = messenger_order.parameter_dict
            stocks = item.stocks.all()

            for param_name in params_dict:
                stocks = stocks.filter(
                    parameters__parameter__name=param_name,
                    parameters__parameter__value=params_dict[param_name]
                )

            stock = stocks.distinct().get()

        else:
            stock = messenger_order.stock

        stock_order = StockOrder.objects.create(
            order=order,
            stock=stock,
            quantity=1
        )

        stock.quantity -= 1
        stock.save(update_fields=['quantity'])

        messenger_order.stock = stock
        messenger_order.order = order
        messenger_order.status = MessengerOrderForm.FormStatus.CONFIRMED
        messenger_order.save(update_fields=['stock', 'order', 'status'])

        # TODO Create final flow Order Success with and details and thanks
        # Create Summary Message

        response_data = response_template()

        response_data = add_message_text(response_data, "Your order has been made! Please monitor your provided contact info. We will reach out to you personally for your order and delivery")

        message = f"Order Details: \n \n"\
                    f"Order Reference ID: {messenger_order.order.id} \n\n" \
                    f"{messenger_order.stock.item.name} \n\n" \
                    f"{messenger_order.provided_name} \n" \
                    f"{messenger_order.address}\n" \
                    f"{messenger_order.contact_details}\n" \

        for param in messenger_order.stock.parameter_list:
            message += '\n'
            for p in param:
                message += f'{p} '

        response_data = add_message_text(response_data, message)

        message = "Thank you for shopping!"
        response_data = add_message_text(response_data, message)

        return Response(response_data, status=status.HTTP_200_OK)







