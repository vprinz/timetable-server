from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(User.object.all())])

    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        user = User.object.create_user(validated_data['email'], validated_data['password'])
        return user
