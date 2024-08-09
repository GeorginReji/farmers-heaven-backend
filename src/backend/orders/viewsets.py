import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, JSONParser

from .filters import OrderFilter, CartFilter
from .models import Cart, Order
from .permissions import OrderPermissions
from .serializers import OrderSerializer, CartSerializer
from ..base import response
from ..base.api.pagination import StandardResultsSetPagination
from ..base.api.viewsets import ModelViewSet
from ..base.services import create_update_record

logger = logging.getLogger(__name__)


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = (OrderPermissions,)
    parser_classes = (JSONParser, MultiPartParser)
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = None

    @swagger_auto_schema(
        method="post",
        operation_summary='Add Item to Cart',
        operation_description='Add Country',
        request_body=CartSerializer,
        response=CartSerializer
    )
    @swagger_auto_schema(
        method="put",
        operation_summary='Update Item to Cart.',
        operation_description='.',
        request_body=CartSerializer,
        response=CartSerializer
    )
    @swagger_auto_schema(
        method="get",
        operation_summary='List of Cart',
        operation_description='',
        response=CartSerializer
    )
    @action(methods=['GET', 'POST', 'PUT'], detail=False, queryset=Cart, filterset_class=CartFilter)
    def cart(self, request):
        if request.method == "GET":
            queryset = Cart.objects.filter(user=request.user.id, is_active=True)
            self.filterset_class = CartFilter
            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response(CartSerializer(page, many=True).data)
            return response.Ok(CartSerializer(queryset, many=True).data)
        else:
            request_data = request.data.copy()
            request_data['user'] = request.user.pk
            return response.Ok(create_update_record(request_data, CartSerializer, Cart))

    @swagger_auto_schema(
        method="post",
        operation_summary='Add Order',
        operation_description='.',
        request_body=OrderSerializer,
        response=OrderSerializer
    )
    @swagger_auto_schema(
        method="put",
        operation_summary='Update Order',
        operation_description='.',
        request_body=OrderSerializer,
        response=OrderSerializer
    )
    @swagger_auto_schema(
        method="get",
        operation_summary='List of Order',
        operation_description='',
        response=OrderSerializer
    )
    @action(methods=['GET', 'POST', 'PUT'], detail=False, queryset=Order, filterset_class=OrderFilter)
    def make_order(self, request):
        if request.method == "GET":
            queryset = Order.objects.filter(user=request.user.id, is_active=True)
            self.filterset_class = OrderFilter
            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response(OrderSerializer(page, many=True).data)
            return response.Ok(OrderSerializer(queryset, many=True).data)
        else:
            request_data = request.data.copy()
            request_data['user'] = request.user.pk
            return response.Ok(create_update_record(request_data, OrderSerializer, Order))
