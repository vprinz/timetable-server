import json

from rest_framework.status import HTTP_200_OK

from common.tests import BaseAPITestCase
from ..factories import TimetableFactory, ClassFactory
from ..models import Timetbale, Class, Subscription, Subgroup
from ..serializers import ClassSerializer


def compare_response_with_sync(updated_ids, deleted_ids):
    result = {
        'updated_ids': updated_ids,
        'deleted_ids': deleted_ids
    }

    return json.dumps(result)


class RestAPIClass(BaseAPITestCase):

    @classmethod
    def setUpClass(cls):
        super(RestAPIClass, cls).setUpClass()
        cls.subscriptions = Subscription.objects.filter(user=cls.user)
        timetable = TimetableFactory(subgroup=cls.subgroup_35_1, type_of_week=Timetbale.DENOMINATOR)
        ClassFactory(timetable=timetable)

    def test_list(self):
        url = self.reverse_with_query_params('classes-list', query_name='timetable_id',
                                             kwargs={'get': self.timetable.id})
        response = self.client.get(url)
        classes = Class.objects.filter(timetable__subgroup__subscription__in=self.subscriptions,
                                       timetable_id=self.timetable.id)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, ClassSerializer(classes, many=True).data)

    def test_list_without_subscription(self):
        subgroup_35_2 = Subgroup.objects.get(group=self.group_35, number='2')
        timetable = TimetableFactory(subgroup=subgroup_35_2, type_of_week=Timetbale.NUMERATOR)
        ClassFactory.create_batch(3, timetable=timetable)
        url = self.reverse_with_query_params('classes-list', query_name='timetable_id',
                                             kwargs={'get': timetable.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, list())
