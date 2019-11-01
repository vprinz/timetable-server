from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND

from .models import UniversityInfo
from .serializers import UniversityInfoSerializer


class UniversityInfoMixin:

    @action(methods=['get'], detail=True)
    def info(self, request, *args, **kwargs):
        instance = self.get_object()
        university_info = UniversityInfo.objects.filter(object_id=instance.id, content_type=instance.content_type())
        if university_info.exists():
            serializer = UniversityInfoSerializer(university_info[0])
            return Response(serializer.data)
        return Response({'detail': 'Not found.'}, status=HTTP_404_NOT_FOUND)
