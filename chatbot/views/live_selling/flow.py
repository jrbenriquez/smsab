from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from chatbot.models.users import MessengerProfile
from chatbot.permissions.manychat import ManyChatAppEntryPermission
from chatbot.serializers.users import MessengerProfileSerializer
from chatbot.responses.manychat.response import response_template
from chatbot.responses.manychat.messages import (add_message_text, add_message_card, create_card_data,
                                                 add_button_to_element, add_message_gallery, add_action_to_element)

from inventory.models.events import Event
from inventory.models.items import Item


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
                    caption=f"Shop Now",
                    target=f"content20200702123449_857707"
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
        data = request.data
        custom_fields = data.get('custom_fields')
        last_browsed_item = None
        if custom_fields:
            last_browsed_item = custom_fields.get('last_browsed_item')
        events = Event.objects.all()
        active_events = [event for event in events if event.is_active]
        response_data = response_template()
        last_product = None
        if last_browsed_item:
            last_product = Item.objects.get(id=last_browsed_item)
        gallery_list = []
        if active_events:
            active_items = Item.objects.none()

            for event in active_events:
                item_relation = event.items_featured.all()
                event_items = Item.objects.filter(events_featured__in=item_relation).order_by('id')

                active_items = active_items | event_items

            if active_items:
                active_items = active_items.order_by('id')
                if last_product:
                    current_items = active_items.filter(id__gt=last_product.id)[:10]
                else:
                    current_items = active_items[:10]
                for item in current_items:
                    item_element = create_card_data(
                        title=item.name,
                        subtitle=f"[₱ {item.price:,.2f}] - {item.description}",
                        image_url=f"{item.get_photo}"
                    )
                    action_data = [
                        {
                            "action": "set_field_value",
                            "field_name": "order_item",
                            "value": f"{item.id}"
                        }
                    ]
                    for data in action_data:
                        item_element = add_button_to_element(
                            item_element,
                            button_type="flow",
                            caption="Get This",
                            target="content20200712140119_187521",
                            action_data=data
                        )

                    gallery_list.append(item_element)

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
                        "target": "content20200712104006_431864"
                    }

                    button_data = [load_more_button,]
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

