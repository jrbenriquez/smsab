import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from api.serializers.items import ItemSerializer, ItemStockSerializer, ItemPhotoSerializer
from inventory.models.items import Item, ItemStock


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser, FormParser]

    @action(methods=['put'], detail=True, permission_classes=[IsAuthenticated],
            url_path='set-featured', url_name='set-featured')
    def set_featured(self, request, pk=None):
        item = Item.objects.get(id=pk)
        item.set_featured()
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stocks = self.perform_create(serializer, data=request.data, files=request.FILES)
        stock_serializer = ItemStockSerializer(stocks, many=True)
        headers = self.get_success_headers(stock_serializer.data)
        return Response(stock_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, data={}, files={}):
        model_obj = serializer.save()

        photo = data.get('photo')
        if photo:
            photo_serializer = ItemPhotoSerializer(data={
                "item": model_obj.id,
                "photo": data.get('photo')
            })
            photo_serializer.is_valid()
            photo_serializer.save()

        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        quantity = data.get('quantity')
        category_id = data.get('category')
        location_id = data.get('location')
        parameter_data = data.get('param_data')
        if isinstance(parameter_data, str):
            parameter_data = json.loads(parameter_data)
        stocks = model_obj.create_item_stocks(
            ItemStockSerializer, price,
            quantity, category_id, location_id,
            parameter_data
        )
        return stocks


