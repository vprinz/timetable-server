import json

from common.tests import BaseAPITestCase
from .models import Faculty
from .factories import FacultyFactory


def compare_faculties_with_response(response):
    faculty_ids = [faculty['id'] for faculty in response]
    faculties = Faculty.objects.filter(id__in=faculty_ids)
    result = []
    for faculty in faculties:
        result.append({
            'id': faculty.id,
            'title': faculty.title,
            'short_title': faculty.short_title
        })

    return result


class RestAPIUniversity(BaseAPITestCase):

    def test_get_all_faculties(self):
        FacultyFactory.create_batch(3)

        url = self.reverse('university-faculties')
        response = self.client.get(url)

        self.assertEqual(json.loads(response.content), compare_faculties_with_response(json.loads(response.content)))
