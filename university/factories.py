import string
import factory.fuzzy

from .models import Faculty, Occupation, Group


class FacultyFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Faculty {0}'.format(n))

    class Meta:
        model = Faculty


class OccupationFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Occupation {0}'.format(n))
    code = factory.fuzzy.FuzzyText(chars=string.digits)

    class Meta:
        model = Occupation


class GroupFactory(factory.DjangoModelFactory):
    title = factory.fuzzy.FuzzyText(length=2, chars=string.digits)
    faculty = factory.SubFactory(FacultyFactory)
    occupation = factory.SubFactory(OccupationFactory)

    class Meta:
        model = Group
