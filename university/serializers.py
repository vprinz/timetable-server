from rest_framework.serializers import ModelSerializer, ReadOnlyField
from rest_framework.validators import UniqueTogetherValidator

from .models import (Faculty, Occupation, Group, Subgroup, Subscription, Timetbale, Class, Lecturer, ClassTime,
                     UniversityInfo)


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
        fields = ('id', 'user', 'title', 'subgroup', 'is_main', 'state')
        extra_kwargs = {'user': {'required': False}}
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
        fields = ('id', 'type_of_week', 'subgroup_id', 'faculty_id', 'state')
        read_only_fields = ('id', 'type_of_week', 'subgroup_id', 'faculty_id', 'state')


class ClassSerializer(ModelSerializer):
    class Meta:
        model = Class
        fields = ('id', 'title', 'type_of_class', 'classroom', 'class_time_id', 'weekday', 'lecturer_id',
                  'timetable_id', 'state')


class LecturerSerializer(ModelSerializer):
    class Meta:
        model = Lecturer
        fields = ('id', 'name', 'patronymic', 'surname', 'state')


class ClassTimeSerializer(ModelSerializer):
    class Meta:
        model = ClassTime
        fields = ('id', 'number', 'start', 'end')

    def to_representation(self, instance):
        response = super(ClassTimeSerializer, self).to_representation(instance)
        response.update({
            'start': instance.start.strftime('%H:%M'),
            'end': instance.end.strftime('%H:%M')
        })
        return response


class UniversityInfoSerializer(ModelSerializer):
    class Meta:
        model = UniversityInfo
        fields = ('id', 'object_id', 'data')
