import json
import base64

from random import randint
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, JSONParser
from django.core.files.base import ContentFile

from .constants import SETTINGS_CONSTANT
from .filters import DynamicSettingsFilter, CountryFilter, StateFilter, CityFilter, ProductsFilter
from .models import DynamicSettings, Country, State, City, UploadedDocument, Products
from .permissions import DynamicSettingsPermissions, UploadedDocumentPermissions
from .serializers import DynamicSettingsSerializer, CountrySerializer, StateSerializer, CitySerializer, \
    UploadedDocumentSerializer, ProductsSerializer
from .services import dropdown_tree, create_presigned_url, get_presigned_url
from ..base import response
from ..base.api.pagination import StandardResultsSetPagination
from ..base.api.viewsets import ModelViewSet
from ..base.services import create_update_record


class UploadedDocumentViewSet(ModelViewSet):
    serializer_class = UploadedDocumentSerializer
    queryset = UploadedDocument.objects.all()
    pagination_class = StandardResultsSetPagination
    permission_classes = (UploadedDocumentPermissions,)
    parser_classes = (JSONParser, MultiPartParser)

    def get_queryset(self):
        queryset = super(UploadedDocumentViewSet, self).get_queryset()
        queryset = queryset.filter(is_active=True)
        return queryset.order_by('-id')

    @action(methods=['POST'], detail=False)
    def create_with_base64(self, request):
        data = request.data.copy()
        img_format, imgstr = data['image'].split(';base64,')
        ext = img_format.split('/')[-1]
        data['image'] = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        serializer = UploadedDocumentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Ok(serializer.data)

    @action(methods=['POST'], detail=False)
    def multiple(self, request):
        data = {"is_active": True}
        result = []
        req_data = json.loads(base64.b64decode(request.data['images']))
        for obj in req_data:
            img_data = obj.get('data', None)
            img_name = obj.get('path', None)
            if img_data and img_name:
                data['image'] = ContentFile(base64.b64decode(img_data), name=img_name.split("/")[-1])
                data['name'] = img_name.split("/")[-1]
                serializer = UploadedDocumentSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                result.append(serializer.data)
        return response.Ok(result)

    @action(methods=['POST'], detail=False)
    def presigned_url(self, request):
        req_data = request.data.copy()
        file_type = req_data["file_type"] if "file_type" in req_data else None
        file_name = req_data["file"] if "file" in req_data else ""
        file_name = file_name.split('/')[-1]
        file_name = str(randint(100000, 999999)) + "_" + file_name
        object_path = 'temp/' + file_name
        if file_type and "file" in req_data:
            return response.Ok({"url": create_presigned_url(object_path, file_type), "file_name": file_name})
        return response.BadRequest({'detail': 'Please provide name of the file'})

    @action(methods=['GET'], detail=False)
    def download_file(self, request):
        path = request.query_params.get('path', None)
        if not path:
            response.BadRequest({'detail': 'Please provide the path of the file!'})
        return response.Ok({"url": get_presigned_url(object_name=path)})


class DynamicSettingsViewSet(ModelViewSet):
    serializer_class = DynamicSettingsSerializer
    queryset = DynamicSettings.objects.all()
    permission_classes = (DynamicSettingsPermissions,)
    parser_classes = (JSONParser, MultiPartParser)
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = None

    def get_queryset(self):
        queryset = super(DynamicSettingsViewSet, self).get_queryset()
        queryset = queryset.filter(is_active=True)
        self.filterset_class = DynamicSettingsFilter
        queryset = self.filter_queryset(queryset)
        return queryset

    @swagger_auto_schema(
        method="get",
        operation_summary='List of dynamic settings',
        operation_description='Admin can get list of all dynamic settings',
        response=DynamicSettingsSerializer
    )
    @action(methods=['GET'], detail=False)
    def dropdown(self, request):
        dropdown_list = SETTINGS_CONSTANT
        data = dropdown_tree(dropdown_list, DynamicSettingsSerializer, DynamicSettings)
        return response.Ok(data)

    @swagger_auto_schema(
        method="post",
        operation_summary='Add Country',
        operation_description='Add Country',
        request_body=CountrySerializer,
        response=CountrySerializer
    )
    @swagger_auto_schema(
        method="put",
        operation_summary='Update Country.',
        operation_description='.',
        request_body=CountrySerializer,
        response=CountrySerializer
    )
    @swagger_auto_schema(
        method="get",
        operation_summary='List of Country',
        operation_description='',
        response=CountrySerializer
    )
    @action(methods=['GET', 'POST', 'PUT'], detail=False, queryset=Country, filterset_class=CountryFilter)
    def country(self, request):
        if request.method == "GET":
            queryset = Country.objects.filter(is_active=True)
            self.filterset_class = CountryFilter
            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response(CountrySerializer(page, many=True).data)
            return response.Ok(CountrySerializer(queryset, many=True).data)
        else:
            return response.Ok(create_update_record(request, CountrySerializer, Country))

    @swagger_auto_schema(
        method="post",
        operation_summary='Add State',
        operation_description='Add State',
        request_body=CountrySerializer,
        response=CountrySerializer
    )
    @swagger_auto_schema(
        method="put",
        operation_summary='Update State.',
        operation_description='.',
        request_body=CountrySerializer,
        response=CountrySerializer
    )
    @swagger_auto_schema(
        method="get",
        operation_summary='List of State',
        operation_description='',
        response=CountrySerializer
    )
    @action(methods=['GET', 'POST', 'PUT'], detail=False, queryset=State, filterset_class=StateFilter)
    def state(self, request):
        if request.method == "GET":
            queryset = State.objects.filter(is_active=True)
            self.filterset_class = StateFilter
            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response(StateSerializer(page, many=True).data)
            return response.Ok(StateSerializer(queryset, many=True).data)
        else:
            return response.Ok(create_update_record(request, StateSerializer, State))

    @swagger_auto_schema(
        method="post",
        operation_summary='Add City',
        operation_description='Add City',
        request_body=CitySerializer,
        response=CitySerializer
    )
    @swagger_auto_schema(
        method="put",
        operation_summary='Update City.',
        operation_description='.',
        request_body=CitySerializer,
        response=CitySerializer
    )
    @swagger_auto_schema(
        method="get",
        operation_summary='List of City',
        operation_description='',
        response=CitySerializer
    )
    @action(methods=['GET', 'POST', 'PUT'], detail=False, queryset=City, filterset_class=CityFilter)
    def city(self, request):
        if request.method == "GET":
            queryset = City.objects.filter(is_active=True)
            self.filterset_class = CityFilter
            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response(CitySerializer(page, many=True).data)
            return response.Ok(CitySerializer(queryset, many=True).data)
        else:
            return response.Ok(create_update_record(request, CitySerializer, City))

    @swagger_auto_schema(
        method="post",
        operation_summary='Add City',
        operation_description='Add City',
        request_body=ProductsSerializer,
        response=ProductsSerializer
    )
    @swagger_auto_schema(
        method="put",
        operation_summary='Update City.',
        operation_description='.',
        request_body=ProductsSerializer,
        response=ProductsSerializer
    )
    @swagger_auto_schema(
        method="get",
        operation_summary='List of City',
        operation_description='',
        response=ProductsSerializer
    )
    @action(methods=['GET', 'POST', 'PUT'], detail=False, queryset=Products, filterset_class=ProductsFilter)
    def products(self, request):
        if request.method == "GET":
            queryset = Products.objects.filter(is_active=True)
            self.filterset_class = ProductsFilter
            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)
            if page is not None:
                return self.get_paginated_response(ProductsSerializer(page, many=True).data)
            return response.Ok(ProductsSerializer(queryset, many=True).data)
        else:
            return response.Ok(create_update_record(request, ProductsSerializer, Products))
