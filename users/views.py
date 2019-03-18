from __future__ import unicode_literals

from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.response import Response

from django.views.generic import View
from django.contrib.auth import login
from django.http import JsonResponse

from .forms import RegistrationForm
from .serializers import UserSerializer


# class RegistrationView(View):
#     def post(self, request):
#         data = request.data
#         form = RegistrationForm(data)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return JsonResponse({'message': 'OK'})
#         return JsonResponse(form.errors, status=HTTP_400_BAD_REQUEST)

class UserCreate(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
