from rest_framework import serializers

from .models import Faculty, Occupation, Group


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ('id', 'title', 'short_title')


class OccupationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occupation
        fields = ('id', 'title', 'short_title', 'code')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('title',)
