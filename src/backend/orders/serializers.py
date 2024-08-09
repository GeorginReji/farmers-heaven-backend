from rest_framework import serializers

from .models import Cart, Order
from ..admin_settings.serializers import ProductsSerializer

from ..base.serializers import ModelSerializer


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class CartSerializer(ModelSerializer):
    product_data = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Cart
        fields = '__all__'

    @staticmethod
    def get_product_data(obj):
        return ProductsSerializer(obj.product).data if obj.product else None
