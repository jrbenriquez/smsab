from rest_framework.viewsets import ModelViewSet
from inventory.models.categories import Category
from rest_framework.permissions import IsAuthenticated
from api.serializers.categories import CategorySerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]