from rest_framework.status import HTTP_200_OK

from common.tests import BaseAPITestCase
from common.utils import TypeWeek
from users.factories import UserFactory

from ..factories import SubscriptionFactory, TimetableFactory
from ..models import Subgroup, Subscription, Timetable
from ..serializers import TimetableSerializer


class RestAPITimetable(BaseAPITestCase):

    def setUp(self):
        super(RestAPITimetable, self).setUp()
        new_user = UserFactory()
        self.subgroup_35_2 = Subgroup.objects.get(group=self.group_35, number='2')
        self.timetable_factory_numerator = TimetableFactory(
            subgroup=self.subgroup_35_2, type_of_week=TypeWeek.numerator.value
        )
        SubscriptionFactory(title='Подписка New User', user=new_user, subgroup=self.subgroup_35_2)

    def test_list(self):
        url = self.reverse('timetables-list')
        response = self.client.get(url)
        subscriptions = Subscription.objects.filter(user=self.user)
        timetable = Timetable.objects.filter(subgroup__subscription__in=subscriptions)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, TimetableSerializer(timetable, many=True).data)

    def test_sync(self):
        timetable = Timetable.objects.get(id=self.timetable.id)
        timetable.state = Timetable.DELETED
        timetable.save()

        url = self.reverse('timetables-sync')
        updated_ids = []
        deleted_ids = [timetable.id]

        self.init_sync(url, updated_ids, deleted_ids)

    def test_meta(self):
        timetables = Timetable.objects.filter(subgroup__subscription__in=[self.subscription])
        url = self.reverse('timetables-meta')

        self.init_meta(url, timetables)
