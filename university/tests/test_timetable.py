import json
import time
from datetime import datetime, timedelta

from rest_framework.status import HTTP_200_OK

from common.tests import BaseAPITestCase
from common.utils import TypeWeek
from users.factories import UserFactory
from ..factories import SubscriptionFactory, TimetableFactory
from ..models import Timetable, Subgroup, Subscription
from ..serializers import TimetableSerializer


class RestAPITimetable(BaseAPITestCase):

    @classmethod
    def setUpClass(cls):
        super(RestAPITimetable, cls).setUpClass()

        new_user = UserFactory()
        cls.subgroup_35_2 = Subgroup.objects.get(group=cls.group_35, number='2')
        cls.timetable_factory_numerator = TimetableFactory(subgroup=cls.subgroup_35_2,
                                                           type_of_week=TypeWeek.numerator.value)
        SubscriptionFactory(title='Подписка New User', user=new_user, subgroup=cls.subgroup_35_2)

    def test_list(self):
        url = self.reverse('timetables-list')
        response = self.client.get(url)
        subscriptions = Subscription.objects.filter(user=self.user)
        timetable = Timetable.objects.filter(subgroup__subscription__in=subscriptions)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, TimetableSerializer(timetable, many=True).data)

    def test_sync(self):
        SubscriptionFactory(title='Подписка на 2 подгруппу', user=self.user, subgroup=self.subgroup_35_2)
        timetable_factory_denominator = TimetableFactory(subgroup=self.subgroup_35_2,
                                                         type_of_week=TypeWeek.denominator.value)

        existing_ids = [t.id for t in Timetable.objects.filter(subgroup__subscription__user=self.user)]
        timestamp = int(datetime.timestamp(datetime.now() + timedelta(seconds=1)))
        data = {'existing_ids': existing_ids, 'timestamp': timestamp}
        url = self.reverse('timetables-sync')

        # If nothing changed
        response = self.client.post(url, json.dumps(data), content_type=self.content_type)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(), self.compare_response_with_sync([], []))
        time.sleep(1)

        # If something changed in subs
        timetable_denominator = Timetable.objects.get(id=timetable_factory_denominator.id)
        timetable_denominator.save()  # just save because nothing to change in timetable (we heed to get new modified)

        timetable_numerator = Timetable.objects.get(id=self.timetable_factory_numerator.id)
        timetable_numerator.delete()

        response = self.client.post(url, json.dumps(data), content_type=self.content_type)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(),
                             self.compare_response_with_sync(updated_ids=[timetable_denominator.id],
                                                             deleted_ids=[self.timetable_factory_numerator.id]))
