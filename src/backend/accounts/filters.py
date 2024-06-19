import django_filters
from django.db.models import Q

from .models import User


class UserBasicFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method='custom_filter')

    class Meta:
        model = User
        fields = {
            'id': ['exact'],
            'first_name': ['icontains'],
            'middle_name': ['icontains'],
            'last_name': ['icontains'],
            'mobile': ['icontains'],
            'email': ['icontains']
        }

    def custom_filter(self, queryset, value):
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value) | Q(middle_name__icontains=value) | Q(
                email__icontains=value) | Q(mobile__icontains=value) | Q(company_name__exact=value) | Q(
                gstin_no__icontains=value))
