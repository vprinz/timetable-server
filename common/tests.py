import json

from rest_framework.reverse import reverse as _reverse
from rest_framework.test import APITestCase

from university.factories import (FacultyFactory, OccupationFactory, GroupFactory, SubgroupFactory, SubscriptionFactory,
                                  TimetableFactory, ClassFactory)
from university.models import Group, Subgroup, Timetbale
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
        cls.timetable = TimetableFactory(subgroup=cls.subgroup_35_1, type_of_week=Timetbale.NUMERATOR)
        cls.class_ = ClassFactory(timetable=cls.timetable)
        cls.subscription = SubscriptionFactory(title='Расписание на 1 семестр.', user=cls.user,
                                               subgroup=cls.subgroup_35_1,
                                               is_main=True)

    def setUp(self):
        self.client.force_login(user=self.user)

    def reverse(self, view_name, args=None, kwargs=None, request=None, format=None, **extra):
        if kwargs is None:
            kwargs = {}
        kwargs.update({'version': self.version})
        return _reverse(view_name, args, kwargs, request, format, **extra)

    def reverse_with_query_params(self, view_name, query_name, *args, **kwargs):
        get = str(kwargs['kwargs'].pop('get', {}))
        url = self.reverse(view_name, *args, **kwargs)
        if get:
            url += f'?{query_name}={get}'
        return url

    def compare_response_with_sync(self, updated_ids, deleted_ids):
        """
        Compare response from the sync request.
        """
        result = {
            'updated_ids': updated_ids,
            'deleted_ids': deleted_ids
        }

        return json.dumps(result)
