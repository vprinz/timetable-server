from rest_framework.decorators import action
from rest_framework.response import Response

from .models import UniversityInfo
from .serializers import UniversityInfoSerializer


class UniversityInfoMixin:

    @action(methods=['get'], detail=True)
    def info(self, request, *args, **kwargs):
        instance = self.get_object()
        university_info = UniversityInfo.objects.filter(object_id=instance.id, content_type=instance.content_type())[0]
        serializer = UniversityInfoSerializer(university_info)
        return Response(serializer.data)
