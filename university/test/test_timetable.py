from rest_framework.status import HTTP_200_OK

from common.tests import BaseAPITestCase
from users.factories import UserFactory
from ..factories import SubscriptionFactory, TimetableFactory
from ..models import Timetbale, Subgroup, Subscription
from ..serializers import TimetableSerializer


class RestAPISubscription(BaseAPITestCase):

    @classmethod
    def setUpClass(cls):
        super(RestAPISubscription, cls).setUpClass()

        new_user = UserFactory()
        cls.subgroup_35_2 = Subgroup.objects.get(group=cls.group_35, number='2')
        TimetableFactory(subgroup=cls.subgroup_35_2, type_of_week=Timetbale.NUMERATOR)
        SubscriptionFactory(title='TEST', user=new_user, subgroup=cls.subgroup_35_2)

    def test_list(self):
        url = self.reverse_with_get('timetables-list', get_name='subgroup_id', kwargs={'get': self.subgroup_35_1.id})
        response = self.client.get(url)
        subscriptions = Subscription.objects.filter(user=self.user)
        timetable = Timetbale.objects.filter(subgroup__subscription__in=subscriptions)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, TimetableSerializer(timetable, many=True).data)
