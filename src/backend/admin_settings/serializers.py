from rest_framework import serializers

from .models import DynamicSettings, Country, State, City, UploadedDocument, Products, ProductImages
from .services import delete_child, get_presigned_url

from ..base.serializers import ModelSerializer
from ..base.services import create_update_manytomany_record


class UploadedDocumentSerializer(ModelSerializer):
    class Meta:
        model = UploadedDocument
        fields = ('id', 'image_path', 'name', 'image', 'is_active')

    def create(self, validated_data):
        validated_data['is_active'] = True
        doc_image = UploadedDocument.objects.create(**validated_data)
        return doc_image


class DynamicSettingsSerializer(ModelSerializer):
    class Meta:
        model = DynamicSettings
        fields = '__all__'

    def update(self, instance, validated_data):
        is_active = validated_data.get('is_active', True)
        if not is_active:
            delete_child(instance, DynamicSettings)
        DynamicSettings.objects.filter(is_active=True, id=instance.pk).update(**validated_data)
        instance = DynamicSettings.objects.filter(id=instance.pk).first()
        return instance


class DynamicSettingsDataSerializer(ModelSerializer):
    class Meta:
        model = DynamicSettings
        fields = ('id', 'value', 'icon', 'is_active')


class CountrySerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

    def validate(self, data):
        name = data.get('name', None)
        location = Country.objects.filter(name=name, is_active=True)
        if self.instance and self.instance.id:
            location = location.exclude(id=self.instance.id)
        if name and location.exists():
            raise serializers.ValidationError({"detail": "Country already exists."})
        return data


class StateBasicDataSerializer(ModelSerializer):
    class Meta:
        model = State
        fields = ('name', 'state_code', 'is_territorial')


class StateSerializer(ModelSerializer):
    country_data = serializers.SerializerMethodField(required=False)

    class Meta:
        model = State
        fields = '__all__'

    def validate(self, data):
        name = data.get('name', None)
        location = State.objects.filter(name=name, is_active=True)
        if self.instance and self.instance.id:
            location = location.exclude(id=self.instance.id)
        if name and location.exists():
            raise serializers.ValidationError({"detail": "State already exists."})
        return data

    @staticmethod
    def get_country_data(obj):
        return CountrySerializer(obj.country).data if obj.country else None


class CityBasicDataSerializer(ModelSerializer):
    class Meta:
        model = City
        fields = ('name', 'state')


class CitySerializer(ModelSerializer):
    state_data = serializers.SerializerMethodField(required=False)

    class Meta:
        model = City
        fields = '__all__'

    def validate(self, data):
        name = data.get('name', None)
        state = data.get('state', None)
        location = City.objects.filter(name=name, state=state, is_active=True)
        if self.instance and self.instance.id:
            location = location.exclude(id=self.instance.id)
        if name and location.exists():
            raise serializers.ValidationError({"detail": "City already exists."})
        return data

    @staticmethod
    def get_state_data(obj):
        return StateSerializer(obj.state).data if obj.state else None


class CountryBasicSerializer(ModelSerializer):
    class Meta:
        model = State
        fields = ('id', 'name')


class StateBasicSerializer(ModelSerializer):
    class Meta:
        model = State
        fields = ('id', 'name',)


class CityBasicSerializer(ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name',)


class DynamicSettingsValueSerializer(ModelSerializer):
    class Meta:
        model = DynamicSettings
        fields = ('value',)


class ProductImagesSerializer(ModelSerializer):
    download_url = serializers.SerializerMethodField(required=False)

    class Meta:
        model = ProductImages
        fields = '__all__'

    @staticmethod
    def get_download_url(obj):
        return get_presigned_url(obj.image) if obj.image else None


class ProductsSerializer(ModelSerializer):
    images = ProductImagesSerializer(many=True)
    category_data = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Products
        fields = '__all__'

    def validate(self, data):
        name = data.get('name', None)
        queryset = Products.objects.filter(name=name, is_active=True)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if name and queryset.exists():
            raise serializers.ValidationError({"detail": "Product already exists."})
        return data

    def create(self, validated_data):
        images_values = create_update_manytomany_record(validated_data.pop("images", []), ProductImages)
        instance = Products.objects.create(**validated_data)
        instance.images.set(images_values)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        images_values = create_update_manytomany_record(validated_data.pop("images", []), ProductImages,
                                                        instance.images)
        Products.objects.filter(id=instance.id).update(**validated_data)
        instance = Products.objects.filter(id=instance.id).first()
        instance.images.set(images_values)
        instance.save()
        return instance

    @staticmethod
    def get_category_data(obj):
        return DynamicSettingsDataSerializer(obj.category).data if obj.category else None
