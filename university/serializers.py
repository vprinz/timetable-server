from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Faculty, Occupation, Group, Subgroup, Subscription


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ('id', 'title', 'short_title')


class OccupationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occupation
        fields = ('id', 'title', 'short_title', 'code')


class SubgroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subgroup
        fields = ('id', 'number')


class GroupSerializer(serializers.ModelSerializer):
    subgroups = SubgroupSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ('number', 'subgroups')


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'name', 'user', 'subgroup', 'is_main')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subgroup'),
            )
        ]
