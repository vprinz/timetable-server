from common.tests import BaseAPITestCase
from .models import Faculty, Occupation, Group
from .factories import FacultyFactory, OccupationFactory, GroupFactory, SubgroupFactory


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


def compare_occupations_with_response(response):
    occupation_ids = [occupation['id'] for occupation in response]
    occupations = Occupation.objects.filter(id__in=occupation_ids)
    result = []
    for occupation in occupations:
        result.append({
            'id': occupation.id,
            'title': occupation.title,
            'short_title': occupation.short_title,
            'code': occupation.code
        })

    return result


def compare_groups_with_response(response):
    group_ids = [group['number'] for group in response]
    groups = Group.objects.filter(number__in=group_ids)
    result = []
    for group in groups:
        result.append({
            'number': group.number,
            'subgroups': [{'id': subgroup.id, 'number': subgroup.number} for subgroup in group.subgroups.all()]
        })

    return result


class RestAPIUniversity(BaseAPITestCase):

    def setUp(self):
        super(RestAPIUniversity, self).setUp()
        self.groups = GroupFactory.create_batch(3)
        self.occupations = OccupationFactory.create_batch(3)
        self.faculties = FacultyFactory.create_batch(3)

    def test_get_all_faculties(self):
        url = self.reverse('university-faculties')
        response = self.client.get(url)

        self.assertEqual(response.data, compare_faculties_with_response(response.data))

    def test_get_occupations_by_faculty_id(self):
        faculty = FacultyFactory(occupations=self.occupations)

        url = self.reverse('university-occupations')
        response = self.client.post(url, {'faculty_id': faculty.id})

        self.assertEqual(response.data, compare_occupations_with_response(response.data))
        self.assertEqual(len(response.data), 3)

    def test_get_groups_by_occupation_id(self):
        occupation = OccupationFactory(groups=self.groups)
        SubgroupFactory.create_batch(2, group=self.groups[0])

        url = self.reverse('university-groups')
        response = self.client.post(url, {'occupation_id': occupation.id})

        self.assertEqual(response.data, compare_groups_with_response(response.data))
