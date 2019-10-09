from rest_framework.serializers import ModelSerializer, ReadOnlyField
from rest_framework.validators import UniqueTogetherValidator

from .models import Faculty, Occupation, Group, Subgroup, Subscription, Timetbale, Class, Lecturer, ClassTime


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
    class Meta:
        model = Group
        fields = ('id', 'number')


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        extra_kwargs = {'user': {'write_only': True}}
        fields = ('id', 'title', 'user', 'subgroup', 'is_main')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subgroup'),
            )
        ]


class TimetableSerializer(ModelSerializer):
    faculty_id = ReadOnlyField(source='get_faculty')

    class Meta:
        model = Timetbale
        fields = ('id', 'type_of_week', 'subgroup_id', 'faculty_id')
        read_only_fields = ('id', 'type_of_week', 'subgroup_id')


class ClassSerializer(ModelSerializer):
    class Meta:
        model = Class
        fields = ('id', 'title', 'type_of_class', 'classroom', 'class_time_id', 'weekday', 'lecturer_id',
                  'timetable_id')


class LecturerSerializer(ModelSerializer):
    class Meta:
        model = Lecturer
        fields = ('id', 'name', 'patronymic', 'surname')


class ClassTimeSerializer(ModelSerializer):
    class Meta:
        model = ClassTime
        fields = ('id', 'number', 'start', 'end')
