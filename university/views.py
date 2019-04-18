from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from common.decorators import required_params
from .models import Faculty, Occupation, Group, Subgroup, Subscription
from .serializers import FacultySerializer, OccupationSerializer, GroupSerializer, SubscriptionSerializer


class UniversityAPIView(GenericViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

    @action(methods=['get'], detail=False)
    def faculties(self, request, *args, **kwargs):
        serializer = FacultySerializer(self.queryset, many=True)
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

    @action(methods=['post'], detail=False, url_path='add-subscription')
    def add_subscription(self, request, *args, **kwargs):
        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(serializer.data)
