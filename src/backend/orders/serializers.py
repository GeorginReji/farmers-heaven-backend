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

    def validate(self, data):
        product = data.get('product', None)
        if not product:
            raise serializers.ValidationError({"detail": "product is required."})
        return data

    def create(self, validated_data):
        user = validated_data.get('user')
        product = validated_data.get('product')
        quantity = validated_data.get('quantity', 1)
        old_instance = Cart.objects.filter(user=user, product=product, is_active=True).first()
        if old_instance:
            old_instance.quantity = old_instance.quantity + quantity
            old_instance.save()
            return Cart.objects.filter(id=old_instance.id).first()
        instance = Cart.objects.create(**validated_data)
        return instance

    @staticmethod
    def get_product_data(obj):
        return ProductsSerializer(obj.product).data if obj.product else None
