from rest_framework.test import APITestCase
from rest_framework.reverse import reverse as _reverse

from users.factories import UserFactory


class BaseAPITestCase(APITestCase):
    version = 'v1'
    content_type = 'application/json'

    @classmethod
    def setUpClass(cls):
        super(BaseAPITestCase, cls).setUpClass()
        cls.user = UserFactory()

    def setUp(self):
        self.client.force_login(user=self.user)

    def reverse(self, view_name, args=None, kwargs=None, request=None, format=None, **extra):
        if kwargs is None:
            kwargs = {}
        kwargs.update({'version': self.version})
        return _reverse(view_name, args, kwargs, request, format, **extra)
