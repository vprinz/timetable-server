from rest_framework.status import HTTP_200_OK

from common.tests import BaseAPITestCase
from common.utils import TypeWeek
from ..factories import TimetableFactory, ClassFactory
from ..models import Class, Subscription, Subgroup
from ..serializers import ClassSerializer


class RestAPIClass(BaseAPITestCase):

    def setUp(self):
        super(RestAPIClass, self).setUp()
        self.subscriptions = Subscription.objects.filter(user=self.user)
        timetable = TimetableFactory(subgroup=self.subgroup_35_1, type_of_week=TypeWeek.denominator.value)
        self.class_theory_games_factory = ClassFactory(title='Теория игр (для self.user)', timetable=timetable)

    def test_list(self):
        url = self.reverse_with_query_params('classes-list', query_name='timetable_id',
                                             kwargs={'get': self.timetable.id})
        response = self.client.get(url)
        classes = Class.objects.filter(timetable_id=self.timetable.id)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, ClassSerializer(classes, many=True).data)

    def test_list_without_subscription(self):
        subgroup_35_2 = Subgroup.objects.get(group=self.group_35, number='2')
        timetable = TimetableFactory(subgroup=subgroup_35_2, type_of_week=TypeWeek.numerator.value)
        classes = ClassFactory.create_batch(3, timetable=timetable)
        url = self.reverse_with_query_params('classes-list', query_name='timetable_id',
                                             kwargs={'get': timetable.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, ClassSerializer(classes, many=True).data)
        self.assertEqual(set(data['timetable_id'] for data in response.data), {timetable.id})

    def test_sync(self):
        first_class = Class.objects.get(id=self.class_delphi.id)
        first_class.classroom = '123'
        first_class.save()

        second_class = Class.objects.get(id=self.class_theory_games_factory.id)
        second_class.state = Class.DELETED
        second_class.save()

        url = self.reverse('classes-sync')
        updated_ids = [first_class.id]
        deleted_ids = [second_class.id]

        self.init_sync(url, updated_ids, deleted_ids)

    def test_meta(self):
        classes = Class.objects.filter(timetable__subgroup__subscription__in=self.subscriptions)
        url = self.reverse('classes-meta')

        self.init_meta(url, classes)
