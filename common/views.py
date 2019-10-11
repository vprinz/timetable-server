from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from common.decorators import login_not_required
from university.models import Faculty


@login_not_required
def home_page(request):
    return render(request, 'home.html')


class UniversityInfo(APIView):

    def get(self, request, *args, **kwargs):
        result = list()
        for faculty in Faculty.objects.all():
            result.append({'faculty_id': faculty.id, 'type_of_week': 0})
        return Response(result)
