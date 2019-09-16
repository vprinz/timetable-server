import string
from datetime import datetime

import factory.fuzzy
import pytz

from users.factories import UserFactory
from .models import Faculty, Occupation, Group, Subgroup, Subscription, Timetbale, Lecturer, Class


class FacultyFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Faculty {0}'.format(n))

    class Meta:
        model = Faculty


class OccupationFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Occupation {0}'.format(n))
    code = factory.fuzzy.FuzzyText(length=10, chars=string.digits)
    faculty = factory.SubFactory(FacultyFactory)

    class Meta:
        model = Occupation


class GroupFactory(factory.DjangoModelFactory):
    number = factory.fuzzy.FuzzyText(length=10, chars=string.digits)
    occupation = factory.SubFactory(OccupationFactory)

    class Meta:
        model = Group


class SubgroupFactory(factory.DjangoModelFactory):
    number = factory.fuzzy.FuzzyText(length=1, chars=string.digits)
    group = factory.SubFactory(GroupFactory)

    class Meta:
        model = Subgroup


class SubscriptionFactory(factory.DjangoModelFactory):
    title = factory.fuzzy.FuzzyText(length=20)
    user = factory.SubFactory(UserFactory)
    subgroup = factory.SubFactory(Subgroup)
    is_main = False

    class Meta:
        model = Subscription


class TimetableFactory(factory.DjangoModelFactory):
    type_of_week = factory.fuzzy.FuzzyInteger(low=0, high=1)
    subgroup = factory.SubFactory(SubgroupFactory)
    created_timestamp = factory.fuzzy.FuzzyDateTime(datetime(2019, 5, 31, tzinfo=pytz.UTC), datetime.now(pytz.UTC))
    modified_timestamp = factory.fuzzy.FuzzyDateTime(datetime(2019, 5, 31, tzinfo=pytz.UTC), datetime.now(pytz.UTC))

    class Meta:
        model = Timetbale


class LecturerFactory(factory.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=64)
    patronymic = factory.fuzzy.FuzzyText(length=64)
    surname = factory.fuzzy.FuzzyText(length=64)

    class Meta:
        model = Lecturer


class ClassFactory(factory.DjangoModelFactory):
    title = factory.fuzzy.FuzzyText(length=150)
    type_of_class = factory.fuzzy.FuzzyInteger(low=0, high=1)
    classroom = factory.fuzzy.FuzzyText(length=10)
    weekday = factory.fuzzy.FuzzyInteger(low=1, high=7)
    lecturer = factory.SubFactory(LecturerFactory)
    timetable = factory.SubFactory(TimetableFactory)
    created_timestamp = factory.fuzzy.FuzzyDateTime(datetime(2019, 5, 31, tzinfo=pytz.UTC), datetime.now(pytz.UTC))
    modified_timestamp = factory.fuzzy.FuzzyDateTime(datetime(2019, 5, 31, tzinfo=pytz.UTC), datetime.now(pytz.UTC))

    class Meta:
        model = Class
