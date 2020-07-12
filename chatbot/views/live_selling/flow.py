from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from chatbot.models.users import MessengerProfile
from chatbot.permissions.manychat import ManyChatAppEntryPermission
from chatbot.serializers.users import MessengerProfileSerializer
from chatbot.responses.manychat.response import response_template
from chatbot.responses.manychat.messages import add_message_text, add_message_card


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

        response_data = add_message_card(response_template(),
                                         title="Welcome to SM Shop and Bags")

        return Response(response_data, status=status.HTTP_200_OK)
