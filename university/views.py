from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Faculty, Occupation


class FacultyView(APIView):
    queryset = Faculty

    def get(self, request, *args, **kwargs):
        return Response('Hello')
