import string
import factory.fuzzy

from .models import Faculty, Occupation, Group, Subgroup


class FacultyFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Faculty {0}'.format(n))
    short_title = factory.fuzzy.FuzzyText(length=10)

    class Meta:
        model = Faculty

    @factory.post_generation
    def occupations(self, create, extracted, **kwargs):
        if create and extracted:
            for extract in extracted:
                self.occupations.add(extract)


class OccupationFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Occupation {0}'.format(n))
    short_title = factory.fuzzy.FuzzyText(length=16)
    code = factory.fuzzy.FuzzyText(length=10, chars=string.digits)

    class Meta:
        model = Occupation

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if create and extracted:
            for extract in extracted:
                self.groups.add(extract)


class GroupFactory(factory.DjangoModelFactory):
    number = factory.fuzzy.FuzzyText(length=2, chars=string.digits)

    class Meta:
        model = Group


class SubgroupFactory(factory.DjangoModelFactory):
    number = factory.fuzzy.FuzzyText(length=1, chars=string.digits)
    groups = factory.SubFactory(GroupFactory)

    class Meta:
        model = Subgroup
