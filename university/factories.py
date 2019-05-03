import string
import factory.fuzzy

from users.factories import UserFactory
from .models import Faculty, Occupation, Group, Subgroup, Subscription


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
    number = factory.fuzzy.FuzzyText(length=2, chars=string.digits)
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
