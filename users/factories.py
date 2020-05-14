import string
from datetime import datetime

import factory.fuzzy
import pytz

from users.models import Device, User


class UserFactory(factory.DjangoModelFactory):
    email = factory.fuzzy.FuzzyText(length=30, suffix='@yandex.ru', chars=string.ascii_lowercase + string.digits)
    password = factory.PostGenerationMethodCall('set_password', 'Timetable123')

    class Meta:
        model = User


class DeviceFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    token = factory.fuzzy.FuzzyText(length=255)
    platform = Device.iOS
    last_update = factory.fuzzy.FuzzyDateTime(datetime(2019, 5, 31, tzinfo=pytz.UTC), datetime.now(pytz.UTC))

    class Meta:
        model = Device
