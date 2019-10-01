import json
import time
from datetime import datetime, timedelta

from rest_framework.status import HTTP_200_OK

from common.tests import BaseAPITestCase
from users.factories import UserFactory
from ..factories import TimetableFactory, ClassFactory, SubscriptionFactory
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
        cls.class_theory_games_factory = ClassFactory(title='Теория игр (для self.user)', timetable=timetable)

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
        # Class for other user. This class_id shouldn't be in response.
        new_user = UserFactory()
        subgroup_35_2 = Subgroup.objects.get(group=self.group_35, number='2')
        SubscriptionFactory(subgroup=subgroup_35_2, user=new_user)
        timetable_factory_denominator = TimetableFactory(subgroup=subgroup_35_2, type_of_week=Timetbale.DENOMINATOR)
        ClassFactory(title='Физика', timetable=timetable_factory_denominator)

        # Class for self.user. This class_id should be in response.
        class_math_factory = ClassFactory(title='Мат. анализ (для self.user)', timetable=self.timetable)
        existing_ids = [t.id for t in Class.objects.filter(timetable__subgroup__subscription__user=self.user)]
        timestamp = int(datetime.timestamp(datetime.now() + timedelta(seconds=1)))
        data = {'existing_ids': existing_ids, 'timestamp': timestamp}
        url = self.reverse('classes-sync')

        # If nothing changed
        response = self.client.post(url, json.dumps(data), content_type=self.content_type)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(), self.compare_response_with_sync([], []))
        time.sleep(1)

        # If something changed
        class_theory_games = Class.objects.get(id=self.class_theory_games_factory.id)
        class_theory_games.classroom = '123'
        class_theory_games.save()

        class_math = Class.objects.get(id=class_math_factory.id)
        class_math.delete()

        response = self.client.post(url, json.dumps(data), content_type=self.content_type)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(),
                             self.compare_response_with_sync(updated_ids=[class_theory_games.id],
                                                             deleted_ids=[class_math_factory.id]))
