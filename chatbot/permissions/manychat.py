from django.conf import settings

from rest_framework import permissions

from chatbot.models.users import MessengerProfile
from chatbot.serializers.users import MessengerProfileSerializer


class ManyChatAppGETPermission(permissions.BasePermission):
    message = 'Invalid App or User Not Found'

    def has_permission(self, request, view):
        user_id = request.data.get('user_id', None)
        app_id = request.META.get('HTTP_X_APP_ID', None)

        valid_apps = settings.MANYCHAT_APP_IDS
        if app_id not in valid_apps:
            return False

        return True


class ManyChatAppPermission(permissions.BasePermission):
    message = 'Invalid App or User Not Found'

    def has_permission(self, request, view):
        user_id = request.data.get('user_id', None)
        app_id = request.META.get('HTTP_X_APP_ID', None)

        valid_apps = settings.MANYCHAT_APP_IDS
        if app_id not in valid_apps:
            return False

        if not user_id:
            return False

        serializer = MessengerProfileSerializer(data=request.data)
        profile_found = not serializer.is_valid(raise_exception=False)
        # Update profile if possible
        if profile_found:
            profile = MessengerProfile.objects.filter(user_id=user_id).first()
            if not profile:
                return False
        else:
            serializer.save()
        return True
