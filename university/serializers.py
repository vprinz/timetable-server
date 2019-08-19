from rest_framework.serializers import ModelSerializer, ReadOnlyField
from rest_framework.validators import UniqueTogetherValidator

from .models import Faculty, Occupation, Group, Subgroup, Subscription, Timetbale, Class, Lecturer


class FacultySerializer(ModelSerializer):
    class Meta:
        model = Faculty
        fields = ('id', 'title')


class OccupationSerializer(ModelSerializer):
    class Meta:
        model = Occupation
        fields = ('id', 'title', 'code')


class SubgroupSerializer(ModelSerializer):
    class Meta:
        model = Subgroup
        fields = ('id', 'number')


class GroupSerializer(ModelSerializer):
    subgroups = SubgroupSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ('number', 'subgroups')


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'title', 'user', 'subgroup', 'is_main')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subgroup'),
            )
        ]


class LecturerSerializer(ModelSerializer):
    class Meta:
        model = Lecturer
        fields = ('name', 'patronymic', 'surname')


class ClassSerializer(ModelSerializer):
    lecturer = LecturerSerializer(required=False, read_only=True)

    class Meta:
        model = Class
        fields = ('title', 'type_of_class', 'classroom', 'class_time', 'weekday', 'lecturer')


class TimetableSerializer(ModelSerializer):
    classes = ReadOnlyField(source='get_classes')

    class Meta:
        model = Timetbale
        fields = ('type_of_week', 'classes')
        read_only_fields = ('type_of_week', 'classes')
