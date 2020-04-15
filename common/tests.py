import json
from datetime import datetime, timedelta

from rest_framework.reverse import reverse as _reverse
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APITestCase

from common.utils import TypeWeek
from university.factories import (
    FacultyFactory, OccupationFactory, GroupFactory, SubgroupFactory,
    SubscriptionFactory, TimetableFactory, ClassFactory
)
from university.models import Group, Subgroup
from users.factories import UserFactory


class BaseAPITestCase(APITestCase):
    version = 'v1'
    content_type = 'application/json'

    @classmethod
    def setUpClass(cls):
        super(BaseAPITestCase, cls).setUpClass()
        FacultyFactory.create_default()
        OccupationFactory.create_default()
        GroupFactory.create_default()
        SubgroupFactory.create_default()

        cls.user = UserFactory(email='super_test_user@kubsu.com')

        cls.group_35 = Group.objects.get(number='35')
        cls.subgroup_35_1 = Subgroup.objects.get(group=cls.group_35, number='1')
        cls.timetable = TimetableFactory(subgroup=cls.subgroup_35_1, type_of_week=TypeWeek.numerator.value)
        cls.class_delphi = ClassFactory(title='Программирование в Delphi (для self.user)', timetable=cls.timetable)
        cls.subscription = SubscriptionFactory(
            title='Расписание на 1 семестр.', user=cls.user, subgroup=cls.subgroup_35_1, is_main=True
        )

    def setUp(self):
        self.client.force_login(user=self.user)

    @classmethod
    def reverse(cls, view_name, args=None, kwargs=None, request=None, format=None, **extra):
        if kwargs is None:
            kwargs = {}
        kwargs.update({'version': cls.version})
        return _reverse(view_name, args, kwargs, request, format, **extra)

    def reverse_with_query_params(self, view_name, query_name, *args, **kwargs):
        get = str(kwargs['kwargs'].pop('get', {}))
        url = self.reverse(view_name, *args, **kwargs)
        if get:
            url += f'?{query_name}={get}'
        return url

    # -------- TEST FOR SYNC --------

    def compare_sync(self, updated_ids, deleted_ids):
        """
        Compare response from the sync request.
        """
        result = {
            'updated_ids': updated_ids,
            'deleted_ids': deleted_ids
        }

        return json.dumps(result)

    def init_sync(self, url, updated_ids, deleted_ids):
        timestamp = int(datetime.timestamp(datetime.now() - timedelta(seconds=5)))
        data = {
            'already_handled': [],
            'timestamp': timestamp
        }

        response = self.client.post(url, json.dumps(data), content_type=self.content_type)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(), self.compare_sync(updated_ids, deleted_ids))

    # -------- END TEST FOR SYNC ----
