from datetime import datetime

from django.db.models import Case, When, Value, BooleanField
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from common.mixins import LoginNotRequiredMixin, SyncMixin, required_params
from .models import Faculty, Occupation, Group, Subgroup, Subscription, Timetbale, Class, Lecturer, ClassTime
from .serializers import (FacultySerializer, OccupationSerializer, GroupSerializer, SubgroupSerializer,
                          SubscriptionSerializer, TimetableSerializer, ClassSerializer, LecturerSerializer,
                          ClassTimeSerializer)


class UniversityAPIView(LoginNotRequiredMixin, GenericViewSet):
    @action(methods=['get'], detail=False)
    def faculties(self, request, *args, **kwargs):
        queryset = Faculty.objects.all()
        serializer = FacultySerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def occupations(self, request, *args, **kwargs):
        faculty_id = request.GET.get('faculty_id')
        instance = Occupation.objects.filter(faculty_id=faculty_id)
        serializer = OccupationSerializer(instance, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def groups(self, request, *args, **kwargs):
        occupation_id = request.GET.get('occupation_id')
        instance = Group.objects.filter(occupation_id=occupation_id)
        serializer = GroupSerializer(instance, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def subgroups(self, request, *args, **kwargs):
        group_id = request.GET.get('group_id')
        instance = Subgroup.objects.filter(group_id=group_id)
        serializer = SubgroupSerializer(instance, many=True)
        return Response(serializer.data)

    @required_params
    @action(methods=['post'], detail=False, url_path='diff')
    def diff_basename(self, request, timestamp, *args, **kwargs):
        """
        :param timestamp: the time at which the result is returned.
        :return: list of base_names which were changed.
        """
        result = list()
        date_time = datetime.fromtimestamp(timestamp)
        models = {
            Subscription: 'subscriptions',
            Timetbale: 'timetables',
            Lecturer: 'lecturers',
            Class: 'classes'
        }
        for model, basename in models.items():
            changes = model.objects.all(). \
                annotate(changed=Case(When(modified__gt=date_time, then=Value(True)), default=Value(False),
                                      output_field=BooleanField())). \
                values_list('changed', flat=True)
            if True in changes:
                result.append(basename)

        return Response(result, headers={'timestamp': int(datetime.timestamp(datetime.now()))})


class SubscriptionAPIView(ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_object(), request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class TimetableAPIView(ListModelMixin, GenericViewSet):
    queryset = Timetbale.objects.all()
    serializer_class = TimetableSerializer

    def list(self, request, *args, **kwargs):
        subgroup_id = request.GET.get('subgroup_id')
        instance = self.get_queryset().filter(subgroup_id=subgroup_id)
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)


class ClassAPIView(SyncMixin, ListModelMixin, GenericViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    def list(self, request, *args, **kwargs):
        timetable_id = request.query_params.get('timetable_id')
        queryset = self.get_queryset().filter(timetable_id=timetable_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LectureAPIView(RetrieveModelMixin, GenericViewSet):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer


class ClassTimeAPIView(RetrieveModelMixin, GenericViewSet):
    queryset = ClassTime.objects.all()
    serializer_class = ClassTimeSerializer
