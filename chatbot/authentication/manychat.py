from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from chatbot.serializers.users import MessengerProfileSerializer


class ManyChatAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        def _perform_create(self, serializer):
            instance = serializer.save()
            return instance

        app_id = request.META.get('HTTP_X_APP_ID', None)
        user_id = request.data.get('user_id', None)

        # Verify App ID in valid APP ID list

        if not user_id:
            return None

        serializer = MessengerProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = _perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


        try:
            user = User.objects.get(username=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)