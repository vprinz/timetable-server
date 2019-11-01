from datetime import datetime

from django.db.models import F, Case, When, Value, BooleanField
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from common.mixins import LoginNotRequiredMixin, SyncMixin, required_params
from . import serializers
from .mixins import UniversityInfoMixin
from .models import (Faculty, Occupation, Group, Subgroup, Subscription, Timetable, Class, Lecturer, ClassTime,
                     UniversityInfo)


class FantasticFourAPIView(UniversityInfoMixin, LoginNotRequiredMixin, ListModelMixin, GenericViewSet):
    pass


class FacultyAPIView(FantasticFourAPIView):
    queryset = Faculty.objects.all()
    serializer_class = serializers.FacultySerializer


class OccupationAPIView(FantasticFourAPIView):
    queryset = Occupation.objects.all()
    serializer_class = serializers.OccupationSerializer

    def get_queryset(self):
        faculty_id = self.request.GET.get('faculty_id')
        return self.queryset.filter(faculty_id=faculty_id)


class GroupAPIView(FantasticFourAPIView):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer

    def get_queryset(self):
        occupation_id = self.request.GET.get('occupation_id')
        return self.queryset.filter(occupation_id=occupation_id)


class SubgroupAPIView(FantasticFourAPIView):
    queryset = Subgroup.objects.all()
    serializer_class = serializers.SubgroupSerializer

    def get_queryset(self):
        group_id = self.request.GET.get('group_id')
        return self.queryset.filter(group_id=group_id)


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
    queryset = Subscription.objects.filter(state=Subscription.ACTIVE)
    serializer_class = serializers.SubscriptionSerializer
    sync_queryset = Subscription.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_destroy(self, instance):
        instance.safe_delete()


class TimetableAPIView(SyncMixin, LoginNotRequiredMixin, ListModelMixin, GenericViewSet):
    queryset = Timetable.objects.filter(state=Class.ACTIVE)
    serializer_class = serializers.TimetableSerializer
    sync_queryset = Timetable.objects.all()

    def get_queryset(self):
        # if subgroup_id is used - get timetables (GET url - /.../timetables/?subgroup_id=<subgroup_id>)
        # if subgroup_id isn't used - for sync/meta methods (POST url - /.../timetables/sync/)
        subgroup_id = self.request.query_params.get('subgroup_id')
        if subgroup_id:
            return self.queryset.filter(subgroup_id=subgroup_id)
        else:
            subscriptions = Subscription.objects.filter(user=self.request.user)
            return self.queryset.filter(subgroup__subscription__in=subscriptions)


class ClassAPIView(SyncMixin, LoginNotRequiredMixin, ListModelMixin, GenericViewSet):
    queryset = Class.objects.filter(state=Class.ACTIVE)
    serializer_class = serializers.ClassSerializer
    sync_queryset = Class.objects.all()

    def get_queryset(self):
        # if timetable_id is used - get classes (GET url - /.../classes/?timetable_id=<timetable_id>)
        # if timetable_id isn't used - for sync/meta methods (POST url - /.../classes/sync/)
        timetable_id = self.request.query_params.get('timetable_id')
        if timetable_id:
            return self.queryset.filter(timetable_id=timetable_id)
        else:
            subscriptions = Subscription.objects.filter(user=self.request.user)
            return self.queryset.filter(timetable__subgroup__subscription__in=subscriptions)


class LectureAPIView(SyncMixin, LoginNotRequiredMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Lecturer.objects.filter(state=Lecturer.ACTIVE)
    serializer_class = serializers.LecturerSerializer
    sync_queryset = Lecturer.objects.all()


class ClassTimeAPIView(LoginNotRequiredMixin, RetrieveModelMixin, GenericViewSet):
    queryset = ClassTime.objects.all()
    serializer_class = serializers.ClassTimeSerializer


class UniversityInfoAPIView(SyncMixin, LoginNotRequiredMixin, ListModelMixin, GenericViewSet):
    queryset = UniversityInfo.objects.filter(state=UniversityInfo.ACTIVE)
    serializer_class = serializers.UniversityInfoSerializer
    sync_queryset = UniversityInfo.objects.all()
