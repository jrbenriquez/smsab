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
                                                 add_button_to_element, add_message_gallery)

from inventory.models.events import Event


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
        gallery_list = []

        for event in active_events:
            event_element = create_card_data(
                title=event.name,
                subtitle=f"{event.description} \n {event.start.strftime('%B %d %-I:%M')} - {event.end.strftime('%B %d %-I:%M')}",
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

        return Response(response_data, status=status.HTTP_200_OK)
