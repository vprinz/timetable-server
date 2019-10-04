import json
import time
from datetime import datetime, timedelta

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from common.tests import BaseAPITestCase
from users.factories import UserFactory
from ..factories import SubscriptionFactory
from ..models import Group, Subgroup, Subscription
from ..serializers import SubscriptionSerializer


class RestAPISubscription(BaseAPITestCase):

    def setUp(self):
        super(RestAPISubscription, self).setUp()
        group_5 = Group.objects.get(number='35')
        group_6 = Group.objects.get(number='36')

        self.subgroup_35_1 = Subgroup.objects.get(group=group_5, number='1', )
        self.subgroup_35_2 = Subgroup.objects.get(group=group_5, number='2', )
        self.subgroup_36_1 = Subgroup.objects.get(group=group_6, number='1', )

        self.student = UserFactory()
        self.not_user_subscription = SubscriptionFactory(title='Timetable', user=self.student,
                                                         subgroup=self.subgroup_36_1)

    def test_create_subscription(self):
        url = self.reverse('subscriptions-list')
        data = {'subgroup': self.subgroup_35_2.id, 'title': 'Test Subscription'}
        response = self.client.post(url, data=json.dumps(data), content_type=self.content_type)

        subscription = Subscription.objects.get(id=response.data['id'])

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.subgroup, self.subgroup_35_2)
        self.assertFalse(subscription.is_main)
        self.assertEqual(response.data, SubscriptionSerializer(subscription).data)

    def test_create_subscription_which_exists(self):
        url = self.reverse('subscriptions-list')
        data = {'subgroup': self.subgroup_35_1.id, 'title': 'User already has this subscription'}
        response = self.client.post(url, data=json.dumps(data), content_type=self.content_type)
        error = json.loads(response.content)['non_field_errors']

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Subscription.objects.filter(user=self.user)), 1)
        self.assertEqual(error, ['unique'])

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
        subscriptions = Subscription.objects.filter(user=self.user)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, SubscriptionSerializer(subscriptions, many=True).data)

    def test_get_subscription_by_id(self):
        url = self.reverse('subscriptions-detail', kwargs={'pk': self.subscription.id})

        response = self.client.get(url)

        subscription = Subscription.objects.get(id=response.data['id'])

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.subgroup, self.subgroup_35_1)
        self.assertTrue(subscription.is_main)
        self.assertEqual(response.data, SubscriptionSerializer(subscription).data)

    def test_get_subscriptions_which_not_belong_to_user(self):
        url = self.reverse('subscriptions-detail', kwargs={'pk': self.not_user_subscription.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_update_subscription(self):
        url = self.reverse('subscriptions-detail', kwargs={'pk': self.subscription.id})
        new_title = 'New title for the subscription'
        data = {'title': new_title, 'is_main': True}
        response = self.client.patch(url, data=json.dumps(data), content_type=self.content_type)

        subscription = Subscription.objects.get(id=response.data['id'])

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.title, new_title)
        self.assertTrue(subscription.is_main)
        self.assertEqual(subscription.subgroup, self.subgroup_35_1)
        self.assertEqual(response.data, SubscriptionSerializer(subscription).data)

    def test_update_subscription_which_not_belong_to_user(self):
        url = self.reverse('subscriptions-detail', kwargs={'pk': self.not_user_subscription.id})
        new_title = 'New title for the subscription'
        data = {'title': new_title}

        response = self.client.patch(url, data=json.dumps(data), content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_sync(self):
        group_36 = Group.objects.get(number='36')
        subgroup_35_2 = Subgroup.objects.get(group=self.group_35, number='2')
        subgroup_36_1 = Subgroup.objects.get(group=group_36, number='1')

        subs_factory_35_2 = SubscriptionFactory(subgroup=subgroup_35_2, user=self.user)
        subs_factory_36_1 = SubscriptionFactory(subgroup=subgroup_36_1, user=self.user)

        existing_ids = [s.id for s in Subscription.objects.filter(user=self.user)]
        timestamp = int(datetime.timestamp(datetime.now() + timedelta(seconds=1)))
        data = {'existing_ids': existing_ids, 'timestamp': timestamp}
        url = self.reverse('subscriptions-sync')

        # If nothing changed
        response = self.client.post(url, json.dumps(data), content_type=self.content_type)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(), self.compare_response_with_sync([], []))
        time.sleep(1)

        # If something changed in subs
        subs_35_2 = Subscription.objects.get(id=subs_factory_35_2.id)
        subs_35_2.is_main = True
        subs_35_2.save()

        subs_36_1 = Subscription.objects.get(id=subs_factory_36_1.id)
        subs_36_1.delete()

        response = self.client.post(url, json.dumps(data), content_type=self.content_type)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(),
                             self.compare_response_with_sync(updated_ids=[subs_35_2.id],
                                                             deleted_ids=[subs_factory_36_1.id]))
