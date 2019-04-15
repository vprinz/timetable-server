from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Faculty, Occupation
from .serializers import FacultySerializer


class FacultyAPIView(GenericViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

    @action(methods=['get'], detail=False)
    def faculties(self, request, *args, **kwargs):
        serializer = FacultySerializer(self.queryset, many=True)
        return Response(serializer.data)


# class OccupationView(APIView):
#
#     def get(self, request):
#         queryset = Occupation.objects.all()
#         occupations = [occupation.title for occupation in queryset]
#         return Response(occupations)
