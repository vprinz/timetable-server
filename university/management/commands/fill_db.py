from django.contrib.auth.hashers import make_password
from django.core.management import BaseCommand

from university.models import Faculty, Group, Occupation, Subgroup
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        password = make_password('82911493p')
        users = [
            {'email': 'valerypavlikov@yandex.ru', 'password': password},
            {'email': 'indrich@mail.com', 'password': password},
            {'email': 'kustodieva@mail.com', 'password': password},
            {'email': 'uglev@mail.com', 'password': password},
        ]
        list(map(lambda user: User.objects.create(**user), users))

        Faculty.objects.create(title='Факультет Компьютерных Технологий и Прикладной Математики')

        occupations = [
            {
                'title': 'Математическое обеспечение и администрирование информационных систем',
                'code': '02.03.03',
                'faculty': Faculty.objects.first()
            },
            {
                'title': 'Фундаментальная информатика и информационные технологии',
                'code': '02.03.02',
                'faculty': Faculty.objects.first()
            }
        ]

        list(map(lambda occupation: Occupation.objects.create(**occupation), occupations))

        groups = [
            {'number': '35', 'occupation': Occupation.objects.get(title=occupations[0]['title'])},
            {'number': '36', 'occupation': Occupation.objects.get(title=occupations[1]['title'])}
        ]

        list(map(lambda group: Group.objects.create(**group), groups))

        subgroups = [
            {'number': '1', 'group': Group.objects.get(number=groups[0]['number'])},
            {'number': '2', 'group': Group.objects.get(number=groups[0]['number'])},
            {'number': '1', 'group': Group.objects.get(number=groups[1]['number'])},
            {'number': '2', 'group': Group.objects.get(number=groups[1]['number'])},
        ]

        list(map(lambda subgroup: Subgroup.objects.create(**subgroup), subgroups))
