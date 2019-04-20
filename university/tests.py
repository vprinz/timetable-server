import json

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from common.tests import BaseAPITestCase
from users.factories import UserFactory
from users.models import User
from .models import Faculty, Occupation, Group, Subscription
from .factories import FacultyFactory, OccupationFactory, GroupFactory, SubgroupFactory, SubscriptionFactory


def compare_faculties_with_response(response):
    faculty_ids = [faculty['id'] for faculty in response]
    faculties = Faculty.objects.filter(id__in=faculty_ids)
    result = []
    for faculty in faculties:
        result.append({
            'id': faculty.id,
            'title': faculty.title,
            'short_title': faculty.short_title
        })

    return result


def compare_occupations_with_response(response):
    occupation_ids = [occupation['id'] for occupation in response]
    occupations = Occupation.objects.filter(id__in=occupation_ids)
    result = []
    for occupation in occupations:
        result.append({
            'id': occupation.id,
            'title': occupation.title,
            'short_title': occupation.short_title,
            'code': occupation.code
        })

    return result


def compare_groups_with_response(response):
    group_ids = [group['number'] for group in response]
    groups = Group.objects.filter(number__in=group_ids)
    result = []
    for group in groups:
        result.append({
            'number': group.number,
            'subgroups': [{'id': subgroup.id, 'number': subgroup.number} for subgroup in group.subgroups.all()]
        })

    return result


class RestAPIUniversity(BaseAPITestCase):

    def test_get_all_faculties(self):
        FacultyFactory.create_batch(3)

        url = self.reverse('university-faculties')
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, compare_faculties_with_response(response.data))

    def test_get_occupations_by_faculty_id(self):
        faculty = FacultyFactory()
        OccupationFactory.create_batch(3, faculty=faculty)

        url = self.reverse('university-occupations')
        response = self.client.post(url, {'faculty_id': faculty.id})

        self.assertEqual(response.status_code, HTTP_200_OK)
        # self.assertEqual(response.data, compare_occupations_with_response(response.data))
        self.assertEqual(len(response.data), 3)

    def test_get_groups_by_occupation_id(self):
        occupation = OccupationFactory()
        groups = GroupFactory.create_batch(2, occupation=occupation)
        SubgroupFactory.create_batch(2, group=groups[0])

        url = self.reverse('university-groups')
        response = self.client.post(url, {'occupation_id': occupation.id})

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, compare_groups_with_response(response.data))


class RestAPISubscription(BaseAPITestCase):

    def setUp(self):
        super(RestAPISubscription, self).setUp()
        self.faculty = FacultyFactory(title='Факультет прикладной математики', short_title='ФПМ')
        self.first_occupation = OccupationFactory(
            title='Математическое обеспечение и администрирование информационных систем',
            short_title='МОиАИС',
            code='02.03.03',
            faculty=self.faculty
        )
        self.second_occupation = OccupationFactory(
            title='Фундаментальная информатика и информационные технологии',
            short_title='ФИиИТ',
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

        self.subscription = SubscriptionFactory(name='Моё расписание на 2 семестр', user=self.user,
                                                subgroup=self.first_subgroup, is_main=True)
        self.subscription_for_student = SubscriptionFactory(name='Timetable', user=self.student,
                                                            subgroup=self.second_subgroup)

    def test_create_subscription(self):
        url = self.reverse('subscription-list')
        data = {'subgroup': self.third_subgroup.id, 'name': 'Test Subscription'}
        response = self.client.post(url, data=json.dumps(data), content_type=self.content_type)

        subscription = Subscription.objects.get(id=response.data['id'])

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.subgroup, self.third_subgroup)
        self.assertFalse(subscription.is_main)

    def test_create_subscription_which_exists(self):
        url = self.reverse('subscription-list')
        data = {'subgroup': self.first_subgroup.id, 'name': 'User already has this subscription'}
        response = self.client.post(url, data=json.dumps(data), content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Subscription.objects.filter(user=self.user)), 1)

    def test_create_subscription_with_not_existing_subgroup(self):
        url = self.reverse('subscription-list')
        data = {'subgroup': 101, 'name': 'This subgroup does not exist'}
        response = self.client.post(url, data=json.dumps(data), content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(len(Subscription.objects.filter(user=self.user)), 1)

    def test_get_all_subscriptions(self):
        url = self.reverse('subscription-list')
        data = {'subgroup': self.third_subgroup.id, 'name': 'Test Subscription'}
        self.client.post(url, data=json.dumps(data), content_type=self.content_type)

        response = self.client.get(url)
        users_id = list(map(lambda item: item['user'], response.data))

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(User.objects.get(id__in=users_id), self.user)

    def test_update_subscription(self):
        url = self.reverse('subscription-detail', kwargs={'pk': self.subscription.id})
        new_name = 'New name for the subscription'
        data = {'name': new_name}
        response = self.client.patch(url, data=json.dumps(data), content_type=self.content_type)

        subscription = Subscription.objects.get(id=response.data['id'])

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.name, new_name)
        self.assertEqual(subscription.subgroup, self.first_subgroup)

    def test_update_subscription_which_not_belong_to_user(self):
        url = self.reverse('subscription-detail', kwargs={'pk': self.subscription_for_student.id})
        new_name = 'New name for the subscription'
        data = {'name': new_name}
        response = self.client.patch(url, data=json.dumps(data), content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(response.content)['detail'], 'Не найдено.')
