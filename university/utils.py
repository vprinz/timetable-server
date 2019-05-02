from users.models import User
from .models import Subgroup, Timetbale


def get_all_classes():
    user = User.objects.get(email='valerypavlikov@yandex.ru')

    timetable = Timetbale.objects.filter(subgroup=user.subscription_set.first())
    return timetable