from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from common.decorators import required_params
from common.mixins import LoginNotRequiredMixin
from .models import Faculty, Occupation, Group, Subgroup, Subscription, Class
from .serializers import (FacultySerializer, OccupationSerializer, GroupSerializer, SubgroupSerializer,
                          SubscriptionSerializer, ClassSerializer)


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


class ClassAPIView(ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    @required_params
    def list(self, request, *args, **kwargs):
        subgroup_id = request.query_params.get('subgroup_id')
        queryset = self.get_queryset().filter(timetable__subgroup_id=subgroup_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
