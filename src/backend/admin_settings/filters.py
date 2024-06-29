import django_filters

from .models import DynamicSettings, Country, State, City, Products


class DynamicSettingsFilter(django_filters.FilterSet):
    parents = django_filters.CharFilter(method='parents_filter', lookup_expr='exact')

    class Meta:
        model = DynamicSettings
        fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains'],
            'value': ['exact', 'icontains'],
            'parent': ['exact']
        }

    def parents_filter(self, queryset, name, value):
        return queryset.filter(parent__in=value.split(","))


class CountryFilter(django_filters.FilterSet):
    class Meta:
        model = Country
        fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains'],
        }


class StateFilter(django_filters.FilterSet):
    class Meta:
        model = State
        fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains'],
            'country': ['exact'],
        }


class CityFilter(django_filters.FilterSet):
    class Meta:
        model = City
        fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains'],
            'state': ['exact'],
        }


class ProductsFilter(django_filters.FilterSet):
    class Meta:
        model = Products
        fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains'],
            'category': ['exact'],
            'description': ['exact', 'icontains'],
            'price': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'stock': ['exact', 'lt', 'lte', 'gt', 'gte'],
        }
