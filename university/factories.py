import string
from datetime import datetime

import factory.fuzzy
import pytz

from common.factories import CommonFactory
from users.factories import UserFactory
from .models import Faculty, Occupation, Group, Subgroup, Subscription, Timetbale, Lecturer, ClassTime, Class


class FacultyFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Faculty {0}'.format(n))
    current_type_of_week = factory.fuzzy.FuzzyInteger(low=0, high=1)

    class Meta:
        model = Faculty

    @classmethod
    def create_default(cls):
        return cls.create(title='Факультет Компьютерных Технологий и Прикладной Математики')


class OccupationFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Occupation {0}'.format(n))
    code = factory.fuzzy.FuzzyText(length=10, chars=string.digits)
    faculty = factory.SubFactory(FacultyFactory)

    class Meta:
        model = Occupation

    @classmethod
    def create_math_occupation(cls):
        title = 'Математическое обеспечение и администрирование информационных систем'
        code = '02.03.03'
        faculty = Faculty.objects.get(title='Факультет Компьютерных Технологий и Прикладной Математики')
        return cls.create(title=title, code=code, faculty=faculty)

    @classmethod
    def create_fundamental_occupation(cls):
        title = 'Фундаментальная информатика и информационные технологии'
        code = '02.03.02'
        faculty = Faculty.objects.get(title='Факультет Компьютерных Технологий и Прикладной Математики')
        return cls.create(title=title, code=code, faculty=faculty)

    @classmethod
    def create_default(cls):
        cls.create_math_occupation()
        cls.create_fundamental_occupation()


class GroupFactory(factory.DjangoModelFactory):
    number = factory.fuzzy.FuzzyText(length=10, chars=string.digits)
    occupation = factory.SubFactory(OccupationFactory)

    class Meta:
        model = Group

    @classmethod
    def create_5_group(cls):
        occupation = Occupation.objects.get(code='02.03.03')
        return cls.create(number='35', occupation=occupation)

    @classmethod
    def create_6_group(cls):
        occupation = Occupation.objects.get(code='02.03.02')
        return cls.create(number='36', occupation=occupation)

    @classmethod
    def create_default(cls):
        cls.create_5_group()
        cls.create_6_group()


class SubgroupFactory(factory.DjangoModelFactory):
    number = factory.fuzzy.FuzzyText(length=1, chars=string.digits)
    group = factory.SubFactory(GroupFactory)

    class Meta:
        model = Subgroup

    @classmethod
    def create_subgroups(cls):
        group_5 = Group.objects.get(number='35')
        numbers = ['1', '2']
        [cls.create(number=n, group=group_5) for n in numbers]

        group_6 = Group.objects.get(number='36')
        numbers = ['1', '2', '3']
        [cls.create(number=n, group=group_6) for n in numbers]

    @classmethod
    def create_default(cls):
        return cls.create_subgroups()


class SubscriptionFactory(CommonFactory):
    title = factory.fuzzy.FuzzyText(length=20)
    user = factory.SubFactory(UserFactory)
    subgroup = factory.SubFactory(Subgroup)
    is_main = False

    class Meta:
        model = Subscription


class TimetableFactory(CommonFactory):
    type_of_week = factory.fuzzy.FuzzyInteger(low=0, high=1)
    subgroup = factory.SubFactory(SubgroupFactory)

    class Meta:
        model = Timetbale


class LecturerFactory(CommonFactory):
    name = factory.fuzzy.FuzzyText(length=64)
    patronymic = factory.fuzzy.FuzzyText(length=64)
    surname = factory.fuzzy.FuzzyText(length=64)

    class Meta:
        model = Lecturer


class ClassTimeFactory(factory.DjangoModelFactory):
    number = factory.fuzzy.FuzzyInteger(low=1, high=8)
    # TODO: refactor to only time (without date)
    start = factory.fuzzy.FuzzyDateTime(datetime(2019, 5, 31, tzinfo=pytz.UTC), datetime.now(pytz.UTC))
    end = factory.fuzzy.FuzzyDateTime(datetime(2019, 5, 31, tzinfo=pytz.UTC), datetime.now(pytz.UTC))

    class Meta:
        model = ClassTime


class ClassFactory(CommonFactory):
    title = factory.fuzzy.FuzzyText(length=150)
    type_of_class = factory.fuzzy.FuzzyInteger(low=0, high=1)
    classroom = factory.fuzzy.FuzzyText(length=10)
    class_time = factory.SubFactory(ClassTimeFactory)
    weekday = factory.fuzzy.FuzzyInteger(low=1, high=7)
    lecturer = factory.SubFactory(LecturerFactory)
    timetable = factory.SubFactory(TimetableFactory)

    class Meta:
        model = Class
