import json
import time
from datetime import datetime, timedelta

from rest_framework.status import HTTP_200_OK

from common.tests import BaseAPITestCase
from university.models import Class
from users.factories import UserFactory
from ..factories import (FacultyFactory, OccupationFactory, GroupFactory, SubgroupFactory, SubscriptionFactory,
                         TimetableFactory, ClassFactory)
from ..models import Faculty, Occupation, Group, Subgroup, Subscription, Timetbale
from ..serializers import (FacultySerializer, OccupationSerializer, GroupSerializer, SubgroupSerializer)


class RestAPIUniversity(BaseAPITestCase):

    def test_get_all_faculties(self):
        FacultyFactory.create_batch(3)
        faculties = Faculty.objects.all()

        url = self.reverse('university-faculties')
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, FacultySerializer(faculties, many=True).data)

    def test_get_occupations_by_faculty_id(self):
        faculty = FacultyFactory()
        OccupationFactory.create_batch(3, faculty=faculty)

        url = self.reverse('university-occupations') + f'?faculty_id={faculty.id}'
        response = self.client.get(url)
        occupations = Occupation.objects.filter(faculty_id=faculty.id)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data, OccupationSerializer(occupations, many=True).data)

    def test_get_groups_by_occupation_id(self):
        occupation = OccupationFactory()
        GroupFactory.create_batch(2, occupation=occupation)

        url = self.reverse('university-groups') + f'?occupation_id={occupation.id}'
        response = self.client.get(url)
        groups = Group.objects.filter(occupation_id=occupation.id)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, GroupSerializer(groups, many=True).data)

    def test_get_subgroups_by_group_id(self):
        group = GroupFactory()
        SubgroupFactory.create_batch(2, group=group)

        url = self.reverse('university-subgroups') + f'?group_id={group.id}'
        response = self.client.get(url)
        subgroups = Subgroup.objects.filter(group_id=group.id)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, SubgroupSerializer(subgroups, many=True).data)

    def test_diff(self):
        # Creating other user with other subscription
        # for checking that diff api returns only base_names for self.user
        user = UserFactory()
        group = Group.objects.get(number='35')
        subgroup = Subgroup.objects.get(number='2', group=group)
        SubscriptionFactory(title='Расписание на 1 семестр.', user=user, subgroup=subgroup)
        timetable_factory = TimetableFactory(subgroup=subgroup, type_of_week=0)
        ClassFactory(timetable=timetable_factory)

        timestamp = int(datetime.timestamp(datetime.now() + timedelta(hours=1)))

        url = self.reverse('university-diff-basename')
        response = self.client.post(url, json.dumps({'timestamp': timestamp}), content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, list())

        time.sleep(1)
        new_timestamp = int(datetime.timestamp(datetime.now()))

        # If there have been changes
        c = Class.objects.get(id=self.class_.id)
        c.classroom = '123'
        c.save()

        s = Subscription.objects.get(id=self.subscription.id)
        s.title = 'New title'
        s.save()

        # Changes for user (these changes shouldn't include to response)
        timetable = Timetbale.objects.get(id=timetable_factory.id)
        timetable.type_of_week = 1
        timetable.save()

        url = self.reverse('university-diff-basename')
        response = self.client.post(url, json.dumps({'timestamp': new_timestamp}),
                                    content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, ['subscriptions', 'classes'])
        self.assertTrue(response.has_header('timestamp'))
