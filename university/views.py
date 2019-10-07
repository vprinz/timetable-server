from datetime import datetime

from django.db.models import F, Case, When, Value, BooleanField
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
            Subscription: {
                'basename': Subscription.basename,
                'related_user_path': 'user'
            },
            Timetbale: {
                'basename': Timetbale.basename,
                'related_user_path': 'subgroup__subscription__user'
            },
            Class: {
                'basename': Class.basename,
                'related_user_path': 'timetable__subgroup__subscription__user'
            },
            Lecturer: {
                'basename': Lecturer.basename,
                'related_user_path': 'class__timetable__subgroup__subscription__user'
            },
        }

        for model, data in models.items():
            changes = model.objects. \
                annotate(changed=Case(When(modified__gt=date_time, then=Value(True)), default=Value(False),
                                      output_field=BooleanField()), u_id=F(data['related_user_path'])). \
                filter(u_id=self.request.user.id). \
                values_list('changed', flat=True)

            if True in changes:
                result.append(data['basename'])

        result.append({'timestamp': int(datetime.timestamp(datetime.now()))})
        return Response(result)


class SubscriptionAPIView(SyncMixin, ModelViewSet):
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

        return Response()


class TimetableAPIView(SyncMixin, ListModelMixin, GenericViewSet):
    queryset = Timetbale.objects.all()
    serializer_class = TimetableSerializer

    def get_queryset(self):
        subscriptions = Subscription.objects.filter(user=self.request.user)
        return self.queryset.filter(subgroup__subscription__in=subscriptions)


class ClassAPIView(SyncMixin, ListModelMixin, GenericViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    def get_queryset(self):
        subscriptions = Subscription.objects.filter(user=self.request.user)
        timetable_id = self.request.query_params.get('timetable_id')
        if timetable_id:
            return self.queryset.filter(timetable__subgroup__subscription__in=subscriptions, timetable_id=timetable_id)
        else:
            return self.queryset.filter(timetable__subgroup__subscription__in=subscriptions)


class LectureAPIView(SyncMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer


class ClassTimeAPIView(RetrieveModelMixin, GenericViewSet):
    queryset = ClassTime.objects.all()
    serializer_class = ClassTimeSerializer
