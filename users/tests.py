import json

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from common.tests import BaseAPITestCase
from .factories import UserFactory
from .models import User


class RestAPIUser(BaseAPITestCase):

    def setUp(self):
        super(RestAPIUser, self).setUp()
        self.user_create_url = self.reverse('users-registration')
        self.user_login_url = self.reverse('users-login')
        self.user_info = self.reverse('users-user-info')
        self.user_logout = self.reverse('users-logout')

    def test_create_user_with_correct_data(self):
        data = json.dumps({'email': 'test-email@mail.com', 'password': 'Timetable123'})
        response = self.client.post(self.user_create_url, data=data, content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_create_user_with_wrong_pass(self):
        data = json.dumps({'email': 'test-email@mail.com', 'password': '1597538291'})
        response = self.client.post(self.user_create_url, data=data, content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['password'], ['password_entirely_numeric'])

    def test_create_user_with_wrong_email(self):
        data = json.dumps({'email': 'test-email', 'password': 'Timetable123'})
        response = self.client.post(self.user_create_url, data=data, content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['email'], ['invalid'])

    def test_create_user_with_exist_email(self):
        data = json.dumps({'email': 'exist_email@mail.com', 'password': 'Timetable123'})
        UserFactory(email='exist_email@mail.com')
        response = self.client.post(self.user_create_url, data=data, content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data['email'], ['unique'])

    def test_create_user_with_no_data(self):
        data = json.dumps({})
        response = self.client.post(self.user_create_url, data=data, content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['email'], ['required'])

    def test_login(self):
        data = json.dumps({'email': self.user.email, 'password': 'Timetable123'})
        response = self.client.post(self.user_login_url, data=data, content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_login_with_wrong_data(self):
        data = json.dumps({'email': self.user.email, 'password': 'Timetable'})
        response = self.client.post(self.user_login_url, data=data, content_type=self.content_type)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['__all__'], ['incorrect_email_or_password'])

    def test_change_user_info(self):
        data = json.dumps({'first_name': 'Nicholas', 'last_name': 'Barnett'})
        response = self.client.patch(self.user_info, data=data, content_type=self.content_type)

        self.assertEqual(User.objects.get(email=self.user.email).get_full_name(), 'Nicholas Barnett')
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_user_logout(self):
        response = self.client.get(self.user_logout)

        self.assertEqual(response.status_code, HTTP_200_OK)