from __future__ import unicode_literals

from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .serializers import UserSerializer
from .models import User


class UserAPIView(ModelViewSet):
    queryset = User.object.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
