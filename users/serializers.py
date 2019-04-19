from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.contrib.auth import password_validation

from .models import User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(User.objects.all())])
    password = serializers.CharField(min_length=8)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password')

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['email'], validated_data['password'])
        return user
