from rest_framework.status import HTTP_200_OK

from common.tests import BaseAPITestCase
from ..factories import ClassTimeFactory
from ..models import Class, ClassTime


class RestAPIClassTimes(BaseAPITestCase):

    def setUp(self):
        super(RestAPIClassTimes, self).setUp()
        self.class_time = ClassTimeFactory()

    def test_get_class_times(self):
        url = self.reverse('class-times-detail', kwargs={'pk': self.class_time.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_sync(self):
        Class.objects.filter(id=self.class_delphi.id).update(class_time=self.class_time)
        class_time = ClassTime.objects.get(id=self.class_time.id)
        class_time.number = 2
        class_time.save()

        url = self.reverse('class-times-sync')
        updated_ids = [class_time.id]
        deleted_ids = []

        self.init_sync(url, updated_ids, deleted_ids)
