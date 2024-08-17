import django_filters

from .models import Order, Cart


class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = {
            'id': ['exact'],
            'user': ['exact'],
            'items': ['exact'],
            'total_amount': ['exact', 'gt', 'lt'],
            'status': ['exact', 'icontains']
        }


class CartFilter(django_filters.FilterSet):
    class Meta:
        model = Cart
        fields = {
            'id': ['exact'],
            'user': ['exact'],
            'product': ['exact'],
            'quantity': ['gt', 'lt'],
        }
