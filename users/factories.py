import string
import factory.fuzzy

from .models import User


class UserFactory(factory.DjangoModelFactory):
    email = factory.fuzzy.FuzzyText(length=30, suffix='@yandex.ru', chars=string.ascii_lowercase + string.digits)
    password = factory.PostGenerationMethodCall('set_password', 'Timetable123')

    class Meta:
        model = User
