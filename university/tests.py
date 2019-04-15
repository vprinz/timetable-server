from rest_framework.test import APITestCase

from django.urls import reverse

from .factories import FacultyFactory, OccupationFactory


class RestAPIUniversity(APITestCase):

    def test_get_all_faculties(self):
        factories = FacultyFactory.create_batch(3)

        url = reverse('faculties')
        response = self.client.get(url)
        faculties = [faculty.title for faculty in factories]

        self.assertEqual(response.data, faculties)

    def test_get_all_occupations(self):
        factories = OccupationFactory.create_batch(3)

        url = reverse('occupations')
        response = self.client.get(url)
        occupations = [occupation.title for occupation in factories]

        self.assertEqual(response.data, occupations)
