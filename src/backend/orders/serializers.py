from rest_framework import serializers

from .models import Cart, Order, OrderProductAmount
from ..admin_settings.serializers import StateBasicSerializer, CityBasicSerializer, \
    ProductsBasicSerializer

from ..base.serializers import ModelSerializer


class OrderProductAmountSerializer(ModelSerializer):
    product_data = serializers.SerializerMethodField(required=False)

    class Meta:
        model = OrderProductAmount
        fields = '__all__'
        extra_kwargs = {
            'amount': {'read_only': True}, 'product': {'required': True},
            'quantity': {'required': True}
        }

    @staticmethod
    def get_product_data(obj):
        return ProductsBasicSerializer(obj.product).data if obj.product else None


class OrderSerializer(ModelSerializer):
    state_data = serializers.SerializerMethodField(required=False)
    city_data = serializers.SerializerMethodField(required=False)
    items = OrderProductAmountSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = {
            'total_amount': {'read_only': True}, 'status': {'read_only': True},
            'address': {'required': True}, 'mobile': {'required': True}, 'pincode': {'required': True}
        }

    def create(self, validated_data):
        total_amount = 0
        product_list = []
        user = validated_data.get('user')
        items = validated_data.pop('items', [])
        items_values = []
        for record in items:
            record.pop('id', None)

            product = record.get('product', None)
            product_list.append(product)

            product_price = product.price or 0
            record['amount'] = product_price
            total_amount += product_price

            items_values.append(OrderProductAmount.objects.create(**record).id)
        validated_data['total_amount'] = total_amount
        instance = Order.objects.create(**validated_data)
        instance.items.set(items_values)
        instance.save()

        # clear cart
        Cart.objects.filter(user=user, product__in=product_list, is_active=True).update(is_active=False)
        return instance

    @staticmethod
    def get_state_data(obj):
        return StateBasicSerializer(obj.state).data if obj.state else None

    @staticmethod
    def get_city_data(obj):
        return CityBasicSerializer(obj.city).data if obj.city else None


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
        return ProductsBasicSerializer(obj.product).data if obj.product else None
