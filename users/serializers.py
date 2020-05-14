from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Device, User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(User.objects.all())])

    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}}
        fields = ('id', 'email', 'first_name', 'last_name', 'password')

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['email'], validated_data['password'])
        return user


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('id', 'token', 'platform', 'version', 'last_update')

    def to_representation(self, instance):
        response = super(DeviceSerializer, self).to_representation(instance)
        response.update({
            'last_update': instance.last_update.strftime('%d-%m-%Y %H:%M:%S')
        })
        return response
