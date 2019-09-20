from datetime import datetime

from django.db.models import Case, When, Value, BooleanField
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from common.decorators import login_not_required
from common.decorators import required_params
from university.models import Subscription, Timetbale, Lecturer, Class


@login_not_required
def home_page(request):
    return render(request, 'home.html')


class DiffBasename(APIView):

    @required_params
    def post(self, request, timestamp, *args, **kwargs):
        result = list()
        date_time = datetime.fromtimestamp(timestamp)
        models = {
            Subscription: 'subscriptions',
            Timetbale: 'timetables',
            Lecturer: 'lecturers',
            Class: 'classes'
        }
        for model, basename in models.items():
            changes = model.objects.all(). \
                annotate(changed=Case(When(modified__gt=date_time, then=Value(True)), default=Value(False),
                                      output_field=BooleanField())). \
                values_list('changed', flat=True)
            if True in changes:
                result.append(basename)

        return Response(result)
