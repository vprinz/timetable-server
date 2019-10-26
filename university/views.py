from datetime import datetime

from django.db.models import F, Case, When, Value, BooleanField
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from common.mixins import LoginNotRequiredMixin, SyncMixin, required_params
from .mixins import UniversityInfoMixin
from .models import (Faculty, Occupation, Group, Subgroup, Subscription, Timetbale, Class, Lecturer, ClassTime,
                     UniversityInfo)
from .serializers import (FacultySerializer, OccupationSerializer, GroupSerializer, SubgroupSerializer,
                          SubscriptionSerializer, TimetableSerializer, ClassSerializer, LecturerSerializer,
                          ClassTimeSerializer, UniversityInfoSerializer)


class FantasticFourAPIView(UniversityInfoMixin, LoginNotRequiredMixin, ListModelMixin, GenericViewSet):
    pass


class FacultyAPIView(FantasticFourAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer


class OccupationAPIView(FantasticFourAPIView):
    queryset = Occupation.objects.all()
    serializer_class = OccupationSerializer

    def get_queryset(self):
        faculty_id = self.request.GET.get('faculty_id')
        return self.queryset.filter(faculty_id=faculty_id)


class GroupAPIView(FantasticFourAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_queryset(self):
        occupation_id = self.request.GET.get('occupation_id')
        return self.queryset.filter(occupation_id=occupation_id)


class SubgroupAPIView(FantasticFourAPIView):
    queryset = Subgroup.objects.all()
    serializer_class = SubgroupSerializer

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
        models = {
            Subscription: {
                'basename': Subscription.basename,
                'related_user_path': Subscription.related_user_path
            },
            Timetbale: {
                'basename': Timetbale.basename,
                'related_user_path': Timetbale.related_user_path
            },
            Class: {
                'basename': Class.basename,
                'related_user_path': Class.related_user_path
            },
            Lecturer: {
                'basename': Lecturer.basename,
                'related_user_path': Lecturer.related_user_path
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


class TimetableAPIView(SyncMixin, LoginNotRequiredMixin, ListModelMixin, GenericViewSet):
    queryset = Timetbale.objects.filter(state=Timetbale.ACTIVE)
    serializer_class = TimetableSerializer

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
    serializer_class = ClassSerializer

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
    serializer_class = LecturerSerializer


class ClassTimeAPIView(LoginNotRequiredMixin, RetrieveModelMixin, GenericViewSet):
    queryset = ClassTime.objects.all()
    serializer_class = ClassTimeSerializer


class UniversityInfoAPIView(SyncMixin, LoginNotRequiredMixin, ListModelMixin, GenericViewSet):
    queryset = UniversityInfo.objects.filter(state=UniversityInfo.ACTIVE)
    serializer_class = UniversityInfoSerializer
