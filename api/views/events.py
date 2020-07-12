from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.serializers.events import EventSerializer, EventPhotoSerializer
from inventory.models.events import Event


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, data={}, files={}):
        model_obj = serializer.save()

        photo = data.get('photo')
        if photo:
            photo_serializer = EventPhotoSerializer(data={
                "event": model_obj.id,
                "photo": data.get('photo')
            })
            photo_serializer.is_valid()
            photo_serializer.save()

        return model_obj