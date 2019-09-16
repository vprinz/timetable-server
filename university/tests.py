import json

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from common.tests import BaseAPITestCase
from users.factories import UserFactory
from .factories import (FacultyFactory, OccupationFactory, GroupFactory, SubgroupFactory, SubscriptionFactory)
from .models import Faculty, Occupation, Group, Subgroup, Subscription


def compare_faculties_with_response(response):
    faculty_ids = [faculty['id'] for faculty in response]
    faculties = Faculty.objects.filter(id__in=faculty_ids)
    result = []
    for faculty in faculties:
        result.append({
            'id': faculty.id,
            'title': faculty.title
        })

    return json.dumps(result)


def compare_occupations_with_response(response):
    occupation_ids = [occupation['id'] for occupation in response]
    occupations = Occupation.objects.filter(id__in=occupation_ids).order_by('-id')
    result = []
    for occupation in occupations:
        result.append({
            'id': occupation.id,
            'title': occupation.title,
            'code': occupation.code
        })

    return json.dumps(result)


def compare_groups_with_response(response):
    group_ids = [group['id'] for group in response]
    groups = Group.objects.filter(id__in=group_ids)
    result = []
    for group in groups:
        result.append({
            'id': group.id,
            'number': group.number
        })

    return json.dumps(result)


def compare_subgroups_with_response(response):
    subgroup_ids = [subgroup['id'] for subgroup in response]
    subgroups = Subgroup.objects.filter(id__in=subgroup_ids)
    result = []
    for subgroup in subgroups:
        result.append({
            'id': subgroup.id,
            'number': subgroup.number
        })

    return json.dumps(result)


class RestAPIUniversity(BaseAPITestCase):

    def test_get_all_faculties(self):
        FacultyFactory.create_batch(3)

        url = self.reverse('university-faculties')
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(), compare_faculties_with_response(response.data))

    def test_get_occupations_by_faculty_id(self):
        faculty = FacultyFactory()
        OccupationFactory.create_batch(3, faculty=faculty)

        url = self.reverse('university-occupations') + f'?faculty_id={faculty.id}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(), compare_occupations_with_response(response.data))
        self.assertEqual(len(response.data), 3)

    def test_get_groups_by_occupation_id(self):
        occupation = OccupationFactory()
        GroupFactory.create_batch(2, occupation=occupation)

        url = self.reverse('university-groups') + f'?occupation_id={occupation.id}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(), compare_groups_with_response(response.data))

    def test_get_subgroups_by_group_id(self):
        group = GroupFactory()
        SubgroupFactory.create_batch(2, group=group)

        url = self.reverse('university-subgroups') + f'?group_id={group.id}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(), compare_subgroups_with_response(response.data))


class RestAPISubscription(BaseAPITestCase):

    def setUp(self):
        super(RestAPISubscription, self).setUp()
        self.faculty = FacultyFactory(title='Факультет прикладной математики')
        self.first_occupation = OccupationFactory(
            title='Математическое обеспечение и администрирование информационных систем',
            code='02.03.03',
            faculty=self.faculty
        )
        self.second_occupation = OccupationFactory(
            title='Фундаментальная информатика и информационные технологии',
            code='02.03.02',
            faculty=self.faculty
        )

        self.first_group = GroupFactory(
            number='35',
            occupation=self.first_occupation
        )
        self.second_group = GroupFactory(
            number='36',
            occupation=self.second_occupation
        )

        self.first_subgroup = SubgroupFactory(
            number='1',
            group=self.first_group
        )
        self.third_subgroup = SubgroupFactory(
            number='2',
            group=self.first_group
        )
        self.second_subgroup = SubgroupFactory(
            number='1',
            group=self.second_group
        )

        self.student = UserFactory()

        self.subscription = SubscriptionFactory(title='Моё расписание на 2 семестр', user=self.user,
                                                subgroup=self.first_subgroup, is_main=True)
        self.not_user_subscription = SubscriptionFactory(title='Timetable', user=self.student,
                                                         subgroup=self.second_subgroup)

    def test_create_subscription(self):
        url = self.reverse('subscriptions-list')
        data = {'subgroup': self.third_subgroup.id, 'title': 'Test Subscription'}
        response = self.client.post(url, data=json.dumps(data), content_type=self.content_type)

        subscription = Subscription.objects.get(id=response.data['id'])

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.subgroup, self.third_subgroup)
        self.assertFalse(subscription.is_main)

    def test_create_subscription_which_exists(self):
        url = self.reverse('subscriptions-list')
        data = {'subgroup': self.first_subgroup.id, 'title': 'User already has this subscription'}
        response = self.client.post(url, data=json.dumps(data), content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Subscription.objects.filter(user=self.user)), 1)

    def test_create_subscription_with_not_existing_subgroup(self):
        url = self.reverse('subscriptions-list')
        data = {'subgroup': 101, 'title': 'This subgroup does not exist'}
        response = self.client.post(url, data=json.dumps(data), content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Subscription.objects.filter(user=self.user)), 1)

    def test_get_all_subscriptions(self):
        url = self.reverse('subscriptions-list')
        data = {'subgroup': self.third_subgroup.id, 'title': 'Test Subscription'}
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
        self.assertEqual(subscription.subgroup, self.first_subgroup)
        self.assertTrue(subscription.is_main)

    def test_get_subscriptions_which_not_belong_to_user(self):
        url = self.reverse('subscriptions-detail', kwargs={'pk': self.not_user_subscription.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content)['detail'], 'Не найдено.')

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
        self.assertEqual(subscription.subgroup, self.first_subgroup)

    def test_update_subscription_which_not_belong_to_user(self):
        url = self.reverse('subscriptions-detail', kwargs={'pk': self.not_user_subscription.id})
        new_title = 'New title for the subscription'
        data = {'title': new_title}
        response = self.client.patch(url, data=json.dumps(data), content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content)['detail'], 'Не найдено.')
