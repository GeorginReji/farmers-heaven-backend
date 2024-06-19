from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import User, Roles
from ..base.api.constants import CUSTOMER_ROLE_SEED_DATA
from ..base.serializers import ModelSerializer


class UserSerializer(ModelSerializer):
    """
    User Serializer
    """

    class Meta:
        model = User
        fields = (
            'id', 'email', 'mobile', "password", 'first_name', 'middle_name', 'last_name', 'username', 'is_superuser'
        )
        extra_kwargs = {'password': {'write_only': True}, 'last_login': {'read_only': True},
                        'is_superuser': {'read_only': True}}


class UserBasicDataSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'middle_name', 'last_name', 'email', 'username', 'mobile', 'dob', 'is_active'
        )


class LoginSerializer(serializers.Serializer):
    """
        login serializer
    """
    username = serializers.CharField(
        allow_blank=False,
        allow_null=False,
        error_messages={'required': 'Please enter a valid mobile/email id.',
                        'blank': 'Please enter a valid mobile/email id.',
                        'null': 'Please enter a valid mobile/email id.'}
    )
    password = serializers.CharField(max_length=128)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(
        min_length=8,
        max_length=128,
        error_messages={'required': 'Please enter a valid password.',
                        'blank': 'Please enter a valid password.',
                        'null': 'Please enter a valid password.',
                        'min_length': 'Password should have minimum 8 characters.'}
    )


class UserRegistrationSerializer(ModelSerializer):
    """
    Don't require email to be unique so visitor can signup multiple times,
    if misplace verification email.  Handle in view.
    """
    email = serializers.EmailField(
        allow_blank=False,
        allow_null=False,
        error_messages={
            'required': 'Please enter a valid e-mail id.',
            'invalid': 'Please enter a valid e-mail id.',
            'blank': 'Please enter a valid e-mail id.',
            'null': 'Please enter a valid e-mail id.'
        },
    )

    class Meta:
        model = get_user_model()
        fields = (
            'id', 'email', 'mobile', "password", 'first_name', 'middle_name', 'last_name', 'username')
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('id',)

    def validate_password(self, value):
        if len(value) > 7:
            return value
        else:
            msg = _('Password should have minimum 8 characters.')
            raise serializers.ValidationError(msg)


class PasswordResetSerializer(serializers.Serializer):
    username = serializers.CharField(
        allow_blank=False,
        allow_null=False,
        error_messages={'required': 'Please enter a valid mobile.',
                        'blank': 'Please enter a valid mobile.',
                        'null': 'Please enter a valid mobile'})


class UserRegisterSerializer(ModelSerializer):
    email = serializers.EmailField(
        allow_blank=False,
        allow_null=False,
        error_messages={
            'required': 'Please enter a valid e-mail id.',
            'invalid': 'Please enter a valid e-mail id.',
            'blank': 'Please enter a valid e-mail id.',
            'null': 'Please enter a valid e-mail id.'
        },
    )

    class Meta:
        model = get_user_model()
        fields = (
            'id', 'email', 'mobile', "password", 'first_name', 'middle_name', 'last_name', 'username'
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('id',)

    def validate_password(self, value):
        if len(value) > 7:
            return value
        else:
            msg = _('Password should have minimum 8 characters.')
            raise serializers.ValidationError(msg)

    def validate(self, data):
        email = data.get('email', None)
        queryset = get_user_model().objects.filter(email=email, is_active=True)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError({'detail': 'Email already in use'})
        return data

    def create(self, validated_data):
        last_name = validated_data.get('first_name', None)
        instance = get_user_model().objects.create_user(**dict(validated_data), is_active=True, last_name=last_name)
        return instance


class UserUpdateSerializer(ModelSerializer):
    email = serializers.EmailField(
        allow_blank=False,
        allow_null=False,
        error_messages={
            'required': 'Please enter a valid e-mail id.',
            'invalid': 'Please enter a valid e-mail id.',
            'blank': 'Please enter a valid e-mail id.',
            'null': 'Please enter a valid e-mail id.'
        },
    )

    class Meta:
        model = get_user_model()
        fields = (
            'id', 'email', 'mobile', "password", 'first_name', 'middle_name', 'last_name', 'username')

    def validate(self, data):
        email = data.get('email', None)
        queryset = get_user_model().objects.filter(email=email, is_active=True)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        if queryset.exists():
            raise serializers.ValidationError({'detail': 'Email already in use'})
        return data
