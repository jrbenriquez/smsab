from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from chatbot.models.users import MessengerProfile
from chatbot.permissions.manychat import ManyChatAppPermission
from chatbot.serializers.users import MessengerProfileSerializer
from chatbot.responses.manychat.response import response_template
from chatbot.responses.manychat.messages import add_message_text


class EntryPointViewSet(ModelViewSet):
    queryset = MessengerProfile.objects.all()
    serializer_class = MessengerProfileSerializer
    permission_classes = [ManyChatAppPermission]
    http_method_names = ['post', 'head']

    def create(self, request, *args, **kwargs):
        data = request.data
        user_id = data.get('user_id')

        profile = MessengerProfile(user_id=user_id)

        # Get many chat template

        # Write custom greeting with user_id
        message = f'Hey there {user_id}'

        response_data = add_message_text(response_template, message)

        return Response(response_data, status=status.HTTP_201_CREATED)



