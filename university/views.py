from datetime import datetime

from django.db.models import F, Case, When, Value, BooleanField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_405_METHOD_NOT_ALLOWED
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from common.mixins import LoginNotRequiredMixin, SyncMixin, required_params
from university import serializers
from university.mixins import UniversityInfoMixin
from university.models import *


class FantasticFourAPIView(UniversityInfoMixin, LoginNotRequiredMixin, ListModelMixin, GenericViewSet):
    filter_backends = (DjangoFilterBackend,)


class FacultyAPIView(FantasticFourAPIView):
    queryset = Faculty.objects.all()
    serializer_class = serializers.FacultySerializer


class OccupationAPIView(FantasticFourAPIView):
    queryset = Occupation.objects.all()
    serializer_class = serializers.OccupationSerializer
    filter_fields = ('faculty_id',)


class GroupAPIView(FantasticFourAPIView):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    filter_fields = ('occupation_id',)


class SubgroupAPIView(FantasticFourAPIView):
    queryset = Subgroup.objects.all()
    serializer_class = serializers.SubgroupSerializer
    filter_fields = ('group_id',)


class UniversityAPIView(GenericViewSet):
    @required_params
    @action(methods=['post'], detail=False, url_path='diff')
    def diff_basename(self, request, timestamp, *args, **kwargs):
        """
        :param timestamp: the time at which the result is returned.
        :return: list of base_names which were changed.
        """
        result = {'base_names': list()}
        date_time = datetime.fromtimestamp(timestamp)
        prefix_user_path = request.user._meta.model_name
        models = {
            Subscription: {
                'basename': Subscription.basename,
                'related_user_path': f'{Subscription.related_subscription_path}{prefix_user_path}'
            },
            Timetable: {
                'basename': Timetable.basename,
                'related_user_path': f'{Timetable.related_subscription_path}{prefix_user_path}'
            },
            Class: {
                'basename': Class.basename,
                'related_user_path': f'{Class.related_subscription_path}{prefix_user_path}'
            },
            Lecturer: {
                'basename': Lecturer.basename,
                'related_user_path': f'{Lecturer.related_subscription_path}{prefix_user_path}'
            },
            ClassTime: {
                'basename': ClassTime.basename,
                'related_user_path': f'{ClassTime.related_subscription_path}{prefix_user_path}'
            }
        }

        for model, data in models.items():
            changes = model.objects. \
                annotate(changed=Case(When(modified__gt=date_time, then=Value(True)), default=Value(False),
                                      output_field=BooleanField()), u_id=F(data['related_user_path'])). \
                filter(u_id=self.request.user.id). \
                values_list('changed', flat=True)

            if True in changes:
                result['base_names'].append(data['basename'])

        university_info_changes = UniversityInfo.objects. \
            annotate(changed=Case(When(modified__gt=date_time, then=Value(True)), default=Value(False),
                                  output_field=BooleanField())).values_list('changed', flat=True)

        if True in university_info_changes:
            result['base_names'].append(UniversityInfo.basename)

        result['timestamp'] = int(datetime.timestamp(datetime.now()))
        return Response(result)


class SubscriptionAPIView(SyncMixin, ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = serializers.SubscriptionSerializer

    def get_queryset(self):
        if self.action == 'sync':
            return self.queryset.filter(user=self.request.user)
        return self.queryset.filter(state=Subscription.ACTIVE, user=self.request.user)

    def perform_destroy(self, instance):
        instance.safe_delete()

    def update(self, request, *args, **kwargs):
        # The subscription update is performed in the method POST.
        return Response(status=HTTP_405_METHOD_NOT_ALLOWED)


class TimetableAPIView(SyncMixin, LoginNotRequiredMixin, ListModelMixin, GenericViewSet):
    queryset = Timetable.objects.all()
    serializer_class = serializers.TimetableSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('subgroup_id',)

    def get_queryset(self):
        subscriptions = Subscription.objects.filter(user=self.request.user)
        if self.action == 'sync':
            return self.queryset.filter(subgroup__subscription__in=subscriptions)
        return self.queryset.filter(subgroup__subscription__in=subscriptions, state=Timetable.ACTIVE)


class ClassAPIView(SyncMixin, LoginNotRequiredMixin, ListModelMixin, GenericViewSet):
    queryset = Class.objects.all()
    serializer_class = serializers.ClassSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('timetable_id',)

    def get_queryset(self):
        subscriptions = Subscription.objects.filter(user=self.request.user)
        if self.action == 'sync':
            return self.queryset.filter(timetable__subgroup__subscription__in=subscriptions)
        return self.queryset.filter(state=Class.ACTIVE)


class LectureAPIView(SyncMixin, LoginNotRequiredMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Lecturer.objects.filter(state=Lecturer.ACTIVE)
    serializer_class = serializers.LecturerSerializer
    sync_queryset = Lecturer.objects.all()


class ClassTimeAPIView(SyncMixin, LoginNotRequiredMixin, RetrieveModelMixin, GenericViewSet):
    queryset = ClassTime.objects.filter(state=ClassTime.ACTIVE)
    serializer_class = serializers.ClassTimeSerializer
    sync_queryset = ClassTime.objects.all()


class UniversityInfoAPIView(SyncMixin, LoginNotRequiredMixin, ListModelMixin, GenericViewSet):
    queryset = UniversityInfo.objects.filter(state=UniversityInfo.ACTIVE)
    serializer_class = serializers.UniversityInfoSerializer
    sync_queryset = UniversityInfo.objects.all()
