from rest_framework.serializers import ModelSerializer, ReadOnlyField

from .models import (Class, ClassTime, Faculty, Group, Lecturer, Occupation,
                     Subgroup, Subscription, Timetable, UniversityInfo)


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
        fields = ('id', 'title', 'subgroup', 'is_main')

    def to_representation(self, instance):
        response = super(SubscriptionSerializer, self).to_representation(instance)
        response.update({
            'user': self.context['request'].user.id,
        })
        return response

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        defaults = {
            'title': validated_data.get('title', str()),
            'is_main': validated_data.get('is_main', False),
            'state': Subscription.ACTIVE
        }
        subscription, created = Subscription.objects.update_or_create(
            user=validated_data['user'], subgroup=validated_data['subgroup'], defaults=defaults
        )
        return subscription


class TimetableSerializer(ModelSerializer):
    faculty_id = ReadOnlyField(source='get_faculty')

    class Meta:
        model = Timetable
        fields = ('id', 'type_of_week', 'subgroup_id', 'faculty_id')
        read_only_fields = ('id', 'type_of_week', 'subgroup_id', 'faculty_id')


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
