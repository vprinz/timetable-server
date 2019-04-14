from rest_framework.test import APITestCase

from django.urls import reverse

from .factories import FacultyFactory


class RestAPIUniversity(APITestCase):

    def test_get_all_faculties(self):
        factories = [FacultyFactory() for _ in range(3)]
        print(factories)

        url = reverse('faculties')
        print(url)
        response = self.client.get(url)
        print(response.data)
