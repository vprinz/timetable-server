from __future__ import unicode_literals
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_201_CREATED

from .factories import UserFactory
from .models import User


class RestAPIUser(APITestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_create_user_with_correct_data(self):
        url = reverse('create-account-list', kwargs={'version': 'v1'})
        response = self.client.post(url, {'email': 'test-email@gmail.com', 'password': '82911493pP'})

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_create_user_with_wrong_pass(self):
        pass

    def test_create_user_with_wrong_email(self):
        pass

    def test_create_user_with_exist_email(self):
        pass

    def test_create_user_with_no_data(self):
        pass
