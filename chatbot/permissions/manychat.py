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


class ManyChatAppEntryPermission(permissions.BasePermission):
    message = 'Invalid App or User Not Found'

    def has_permission(self, request, view):
        app_id = request.META.get('HTTP_X_APP_ID', None)

        valid_apps = settings.MANYCHAT_APP_IDS
        if app_id not in valid_apps:
            return False

        data = request.data
        user_id_info = data.get('key')
        if not user_id_info:
            user_id_info = data.get('manychat').get('key')
            if not user_id_info:
                return False

        try:
            user_id = user_id_info.split(':')[-1]
        except Exception as e:
            return False

        page_id = data.get('page_id')
        status = data.get('status')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        gender = data.get('gender')
        profile_pic = data.get('profile_pic')
        live_chat_url = data.get('live_chat_url')
        phone = data.get('phone')
        email = data.get('email')
        last_interaction = data.get('last_interaction')
        custom_fields = data.get('custom_fields')
        if custom_fields:
            address = custom_fields.get('address')
            provided_name = custom_fields.get('name')
            contact_details = custom_fields.get('contact')

        else:
            address = None
            contact_details = None
            provided_name = None
        profile_data = {
            "user_id": user_id,
            "page_id": page_id,
            "status": status,
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "profile_pic": profile_pic,
            "live_chat_url": live_chat_url,
            "phone": phone,
            "email": email,
            "last_interaction": last_interaction,
            "address": address,
            "contact_details": contact_details
        }

        profile = MessengerProfile.objects.filter(user_id=user_id)
        if not profile:
            serializer = MessengerProfileSerializer(data=profile_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(address=address, contact_details=contact_details, provided_name=provided_name)
        else:
            profile = profile.get()
            serializer = MessengerProfileSerializer(profile, data=profile_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(address=address, contact_details=contact_details, provided_name=provided_name)

        return True
