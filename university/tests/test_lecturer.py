from rest_framework.status import HTTP_200_OK

from common.tests import BaseAPITestCase
from ..factories import LecturerFactory
from ..models import Class, Lecturer
from ..serializers import LecturerSerializer


class RestAPILecturer(BaseAPITestCase):

    def setUp(self):
        super(RestAPILecturer, self).setUp()
        self.lecturer = LecturerFactory()

    def test_get_lecturer(self):
        url = self.reverse('lecturers-detail', kwargs={'pk': self.lecturer.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertDictEqual(response.data, LecturerSerializer(self.lecturer).data)

    def test_sync(self):
        Class.objects.filter(id=self.class_delphi.id).update(lecturer=self.lecturer)
        lecturer = Lecturer.objects.get(id=self.lecturer.id)
        lecturer.name = 'Анатолий'
        lecturer.save()

        url = self.reverse('lecturers-sync')
        updated_ids = [lecturer.id]
        deleted_ids = []

        self.init_sync(url, updated_ids, deleted_ids)

    def test_meta(self):
        lecturers = Lecturer.objects.filter(class__timetable__subgroup__subscription__in=[self.subscription])
        url = self.reverse('lecturers-meta')

        self.init_meta(url, lecturers)
