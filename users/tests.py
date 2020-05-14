import json

from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_400_BAD_REQUEST)

from common.tests import BaseAPITestCase
from users.factories import DeviceFactory, UserFactory
from users.models import Device, User
from users.serializers import DeviceSerializer


class RestAPIUser(BaseAPITestCase):

    @classmethod
    def setUpClass(cls):
        super(RestAPIUser, cls).setUpClass()
        cls.user_create_url = cls.reverse('users-registration')
        cls.user_login_url = cls.reverse('users-login')
        cls.user_info = cls.reverse('users-user-info')
        cls.user_logout = cls.reverse('users-logout')
        cls.user_device = cls.reverse('users-device')

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

    def test_device(self):
        """Case for testing if device doesn't exist."""
        token = 'f6V5isN83Fw:APA91bErGiPse5QZRNYUq4tm38xu1MJ-1koU90AOJdOp'
        data = json.dumps({
            'token': token,
            'platform': Device.IOS,
        })
        response = self.client.patch(self.user_device, data=data, content_type=self.content_type)

        device = Device.objects.get(token=token, platform=Device.IOS)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(), DeviceSerializer(device).data)
        self.assertEqual(User.objects.get(id=self.user.id).device_set.last(), device)

    def test_update_device(self):
        """Case for testing if device exists and needs to update."""
        existing_token = 'ejkjawe:432ksjalde'
        device_factory = DeviceFactory(token=existing_token, user=self.user, version=self.version)
        data = json.dumps({
            'token': existing_token,
            'platform': Device.ANDROID,
        })
        response = self.client.patch(self.user_device, data=data, content_type=self.content_type)

        device = Device.objects.get(id=device_factory.id)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertJSONEqual(response.content.decode(), DeviceSerializer(device).data)
        self.assertEqual(device.platform, Device.ANDROID)
