from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from inventory.models.locations import Location
from api.serializers.locations import LocationSerializer


class LocationViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]