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

    def test_create_user_with_correct_data(self):
        response = self.client.post(self.user_create_url, {'email': 'test-email@mail.com', 'password': 'Timetable123'})

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_create_user_with_wrong_pass(self):
        response = self.client.post(self.user_create_url, {'email': 'test-email@mail.com', 'password': '1597538291'})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['password'][0], 'This password is entirely numeric.')

    def test_create_user_with_wrong_email(self):
        response = self.client.post(self.user_create_url, {'email': 'test-email', 'password': 'Timetable123'})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['email'][0], 'Enter a valid email address.')

    def test_create_user_with_exist_email(self):
        UserFactory(email='exist_email@mail.com')
        response = self.client.post(self.user_create_url, {'email': 'exist_email@mail.com', 'password': 'Timetable123'})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data['email'][0], 'This field must be unique.')

    def test_create_user_with_no_data(self):
        response = self.client.post(self.user_create_url, {})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['email'][0], 'This field is required.')

    def test_login(self):
        response = self.client.post(self.user_login_url, data={'email': self.user.email, 'password': 'Timetable123'})

        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_login_with_wrong_data(self):
        response = self.client.post(self.user_login_url, data={'email': self.user.email, 'password': 'Timetable'})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_change_user_info(self):
        response = self.client.patch(self.user_info, data={'first_name': 'Nicholas', 'last_name': 'Barnett'})

        self.assertEqual(User.objects.get(email=self.user.email).get_full_name(), 'Nicholas Barnett')
        self.assertEqual(response.status_code, HTTP_200_OK)
