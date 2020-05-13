import json

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from common.tests import BaseAPITestCase
from users.factories import UserFactory
from ..factories import SubscriptionFactory
from ..models import Group, Subgroup, Subscription


class RestAPISubscription(BaseAPITestCase):

    def setUp(self):
        super(RestAPISubscription, self).setUp()
        group_5 = Group.objects.get(number='35')
        group_6 = Group.objects.get(number='36')

        self.subgroup_35_1 = Subgroup.objects.get(group=group_5, number='1')
        self.subgroup_35_2 = Subgroup.objects.get(group=group_5, number='2')
        self.subgroup_36_1 = Subgroup.objects.get(group=group_6, number='1')

        self.student = UserFactory()
        self.not_user_subscription = SubscriptionFactory(
            title='Timetable', user=self.student, subgroup=self.subgroup_36_1
        )

    def test_create_subscription(self):
        url = self.reverse('subscriptions-list')
        data = {'subgroup': self.subgroup_35_2.id, 'title': 'Test Subscription'}
        response = self.client.post(url, data=json.dumps(data), content_type=self.content_type)

        subscription = Subscription.objects.get(id=response.data['id'])

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.subgroup, self.subgroup_35_2)
        self.assertFalse(subscription.is_main)

    def test_create_subscription_which_exists(self):
        """Case for testing update subscription. POST as PATCH."""
        url = self.reverse('subscriptions-list')
        data = {'subgroup': self.subgroup_35_1.id, 'title': 'New title'}
        response = self.client.post(url, data=json.dumps(data), content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(len(Subscription.objects.filter(user=self.user)), 1)
        self.assertEqual(Subscription.objects.get(subgroup=self.subgroup_35_1).title, 'New title')

    def test_create_subscription_with_not_existing_subgroup(self):
        url = self.reverse('subscriptions-list')
        data = {'subgroup': 101, 'title': 'This subgroup does not exist'}
        response = self.client.post(url, data=json.dumps(data), content_type=self.content_type)
        error = json.loads(response.content)['subgroup']

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Subscription.objects.filter(user=self.user)), 1)
        self.assertEqual(error, ['does_not_exist'])

    def test_get_all_subscriptions(self):
        url = self.reverse('subscriptions-list')
        data = {'subgroup': self.subgroup_35_2.id, 'title': 'Test Subscription'}
        self.client.post(url, data=json.dumps(data), content_type=self.content_type)

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_subscription_by_id(self):
        url = self.reverse('subscriptions-detail', kwargs={'pk': self.subscription.id})

        response = self.client.get(url)

        subscription = Subscription.objects.get(id=response.data['id'])

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.subgroup, self.subgroup_35_1)
        self.assertTrue(subscription.is_main)

    def test_get_subscriptions_which_not_belong_to_user(self):
        url = self.reverse('subscriptions-detail', kwargs={'pk': self.not_user_subscription.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_sync(self):
        active_subscription = Subscription.objects.get(id=self.subscription.id)
        active_subscription.title = 'Updated title'
        active_subscription.save()

        deleted_subscription_factory = SubscriptionFactory(
            title='My useless subscription', user=self.user, subgroup=self.subgroup_35_2
        )
        deleted_subscription = Subscription.objects.get(id=deleted_subscription_factory.id)
        deleted_subscription.state = Subscription.DELETED
        deleted_subscription.save()

        url = self.reverse('subscriptions-sync')
        updated_ids = [active_subscription.id]
        deleted_ids = [deleted_subscription.id]

        self.init_sync(url, updated_ids, deleted_ids)

    def test_meta(self):
        subscriptions = Subscription.objects.filter(user=self.user)
        url = self.reverse('subscriptions-meta')

        self.init_meta(url, subscriptions)
