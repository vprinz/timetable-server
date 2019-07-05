from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from common.utils import get_model_field_names


class Faculty(models.Model):
    title = models.CharField(max_length=256, unique=True)

    class Meta:
        verbose_name = 'Факультет'
        verbose_name_plural = 'Факультеты'

    def __str__(self):
        return self.title


class Occupation(models.Model):
    title = models.CharField(max_length=256, unique=True)
    code = models.CharField(max_length=10, unique=True)
    faculty = models.ForeignKey(Faculty, related_name='occupations', null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('title', 'code')
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'

    def __str__(self):
        return f'{self.title}'


class Group(models.Model):
    number = models.CharField(max_length=2, primary_key=True)  # TODO убрать primary_key
    occupation = models.ForeignKey(Occupation, related_name='groups', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Группа студента'
        verbose_name_plural = 'Группы студентов'

    def __str__(self):
        return self.number


class Subgroup(models.Model):
    number = models.CharField(max_length=1)
    group = models.ForeignKey(Group, related_name='subgroups', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Подгруппа студента'
        verbose_name_plural = 'Подгруппы студентов'

    def __str__(self):
        return f'{self.group.number}/{self.number}'


class Subscription(models.Model):
    title = models.CharField(max_length=150, null=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    subgroup = models.ForeignKey(Subgroup, on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'subgroup')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return self.title


class Timetbale(models.Model):
    NUMERATOR = 0
    DENOMINATOR = 1

    TYPE_OF_WEEK = (
        (NUMERATOR, 'Числитель'),
        (DENOMINATOR, 'Знаменатель')
    )

    type_of_week = models.SmallIntegerField(choices=TYPE_OF_WEEK)
    subgroup = models.ForeignKey(Subgroup, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('subgroup', 'type_of_week')
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'

    def __str__(self):
        return f'Расписание для {self.subgroup} группы | {self.TYPE_OF_WEEK[self.type_of_week][1]}'


class ClassTime(models.Model):
    number = models.SmallIntegerField()
    start = models.TimeField()
    end = models.TimeField()

    class Meta:
        verbose_name = 'Номер пары'
        verbose_name_plural = 'Номера пар'

    def __str__(self):
        return f'{self.number}-ая пара'


class Lecturer(models.Model):
    name = models.CharField(max_length=64)
    patronymic = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

    def __str__(self):
        return f'{self.name} {self.surname}'


class Class(models.Model):
    PRACTICE = 0
    LECTURE = 1

    TYPE_OF_CLASS = (
        (PRACTICE, 'Практическое занятие'),
        (LECTURE, 'Лекция')
    )

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    WEEKDAYS = (
        (MONDAY, 'Понедельник'),
        (TUESDAY, 'Вторник'),
        (WEDNESDAY, 'Среда'),
        (THURSDAY, 'Четверг'),
        (FRIDAY, 'Пятница'),
        (SATURDAY, 'Суббота'),
        (SUNDAY, 'Воскресенье')
    )

    title = models.CharField(max_length=150)
    type_of_class = models.SmallIntegerField(choices=TYPE_OF_CLASS)
    classroom = models.CharField(max_length=10)
    time_class = models.ForeignKey(ClassTime, on_delete=models.PROTECT)
    weekday = models.SmallIntegerField(choices=WEEKDAYS)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.PROTECT)
    timetable = models.ForeignKey(Timetbale, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'

    def __str__(self):
        return f'{self.title} | {self.timetable.subgroup}'