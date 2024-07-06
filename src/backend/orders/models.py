from django.contrib.auth import get_user_model
from django.db import models

from .constants import ORDER_STATUS, CREATED
from ..admin_settings.models import Products
from ..base.models import TimeStampedModel


class Cart(TimeStampedModel):
    user = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.PROTECT,
                             related_name='cart_user')
    product = models.ForeignKey(Products, blank=True, null=True, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=False)


class OrderProductAmount(TimeStampedModel):
    product = models.ForeignKey(Products, blank=True, null=True, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField(blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=False)


class Order(TimeStampedModel):
    user = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.PROTECT,
                             related_name='order_user')
    items = models.ManyToManyField(OrderProductAmount, blank=True)
    total_amount = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=255, choices=ORDER_STATUS, default=CREATED)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
