import json
import time
from datetime import datetime, timedelta

from rest_framework.status import HTTP_200_OK

from common.tests import BaseAPITestCase
from ..factories import SubscriptionFactory, TimetableFactory, ClassFactory
from ..models import Timetbale, Class, Subscription, Subgroup
from ..serializers import ClassSerializer


def compare_response_with_sync(updated_ids, deleted_ids):
    result = {
        'updated_ids': updated_ids,
        'deleted_ids': deleted_ids
    }

    return json.dumps(result)


class RestAPISubscription(BaseAPITestCase):

    @classmethod
    def setUpClass(cls):
        super(RestAPISubscription, cls).setUpClass()
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

    def test_sync(self):
        subgroup_35_2 = Subgroup.objects.get(group=self.group_35, number='2')
        SubscriptionFactory(subgroup=subgroup_35_2, user=self.user)
        timetable_factory_35_2_numerator = TimetableFactory(subgroup=subgroup_35_2, type_of_week=Timetbale.NUMERATOR)

        subscriptions = Subscription.objects.filter(user=self.user)
        existing_ids = [s.id for s in Timetbale.objects.filter(subgroup__subscription__in=subscriptions)]
        timestamp = int(datetime.timestamp(datetime.now() + timedelta(seconds=1)))
        data = {'existing_ids': existing_ids, 'timestamp': timestamp}
        url = self.reverse('timetables-sync')

        # If nothing changed
        response = self.client.post(url, json.dumps(data), content_type=self.content_type)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(), compare_response_with_sync([], []))
        time.sleep(1)

        # If something changed in timetable
        timetable_35_1_numerator = Timetbale.objects.get(id=self.timetable.id)
        timetable_35_1_numerator.save()  # Just save because can't change something

        timetable_35_2_numerator = Timetbale.objects.get(id=timetable_factory_35_2_numerator.id)
        timetable_35_2_numerator.delete()

        response = self.client.post(url, json.dumps(data), content_type=self.content_type)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(), compare_response_with_sync(
            updated_ids=[timetable_35_1_numerator.id], deleted_ids=[timetable_factory_35_2_numerator.id]))
