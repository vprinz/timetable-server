from __future__ import unicode_literals
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from .factories import UserFactory
from .models import User


class RestAPIUser(APITestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_create_user_with_correct_data(self):
        url = reverse('create-account-list', kwargs={'version': 'v1'})
        response = self.client.post(url, {'email': 'test-email@mail.com', 'password': 'Timetable123'})

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_create_user_with_wrong_pass(self):
        url = reverse('create-account-list', kwargs={'version': 'v1'})
        response = self.client.post(url, {'email': 'test-email@mail.com', 'password': '1597538291'})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['password'][0], 'Введённый пароль состоит только из цифр.')

    def test_create_user_with_wrong_email(self):
        url = reverse('create-account-list', kwargs={'version': 'v1'})
        response = self.client.post(url, {'email': 'test-email', 'password': 'Timetable123'})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['email'][0], 'Введите корректный адрес электронной почты.')

    def test_create_user_with_exist_email(self):
        UserFactory(email='exist_email@mail.com')
        url = reverse('create-account-list', kwargs={'version': 'v1'})
        response = self.client.post(url, {'email': 'exist_email@mail.com', 'password': 'Timetable123'})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data['email'][0], 'Это поле должно быть уникально.')

    def test_create_user_with_no_data(self):
        url = reverse('create-account-list', kwargs={'version': 'v1'})
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['email'][0], 'Это поле обязательно.')
