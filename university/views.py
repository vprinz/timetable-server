from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from common.decorators import required_params
from .models import Faculty, Occupation, Group, Subscription, Timetbale
from .serializers import (FacultySerializer, OccupationSerializer, GroupSerializer, SubscriptionSerializer,
                          TimetableSerializer)


class UniversityAPIView(GenericViewSet):
    @action(methods=['get'], detail=False)
    def faculties(self, request, *args, **kwargs):
        queryset = Faculty.objects.all()
        serializer = FacultySerializer(queryset, many=True)
        return Response(serializer.data)

    @required_params
    @action(methods=['post'], detail=False)
    def occupations(self, request, faculty_id, *args, **kwargs):
        instance = Occupation.objects.filter(faculty=Faculty.objects.get(id=faculty_id))
        serializer = OccupationSerializer(instance, many=True)
        return Response(serializer.data)

    @required_params
    @action(methods=['post'], detail=False)
    def groups(self, request, occupation_id, *args, **kwargs):
        instance = Group.objects.filter(occupation=Occupation.objects.get(id=occupation_id))
        serializer = GroupSerializer(instance, many=True)
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


class TimetableAPIView(GenericViewSet):
    queryset = Timetbale.objects.all()
    serializer_class = TimetableSerializer

    # def get_queryset(self):
    #     return self.queryset.filter(user=self.request.user)

    @action(methods=['post'], detail=False)
    @required_params
    def classes(self, request, subgroup_id, *args, **kwargs):
        queryset = self.get_queryset().filter(subgroup_id=subgroup_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
