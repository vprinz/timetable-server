from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models

from common.models import CommonModel
from common.utils import TypeWeek


class FantasticFourModel(models.Model):
    """
    Main model for four classes which appear during start app.

    (Faculty, Occupation, Group, Subgroup).
    """

    @classmethod
    def content_type(cls):
        return ContentType.objects.get_for_model(cls)

    class Meta:
        abstract = True


class Faculty(FantasticFourModel):
    title = models.CharField(max_length=256, unique=True)

    class Meta:
        verbose_name_plural = 'Faculties'

    def __str__(self):
        return self.title


class Occupation(FantasticFourModel):
    title = models.CharField(max_length=256, unique=True)
    code = models.CharField(max_length=10, unique=True)
    faculty = models.ForeignKey(Faculty, related_name='occupations', null=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('title', 'code')

    def __str__(self):
        return f'{self.title}'


class Group(FantasticFourModel):
    number = models.CharField(max_length=10, unique=True)
    occupation = models.ForeignKey(Occupation, related_name='groups', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Group of student'
        verbose_name_plural = 'Groups of students'

    def __str__(self):
        return self.number


class Subgroup(FantasticFourModel):
    number = models.CharField(max_length=1)
    group = models.ForeignKey(Group, related_name='subgroups', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Subgroup of student'
        verbose_name_plural = 'Subgroups of students'

    def __str__(self):
        return f'{self.group.number}/{self.number}'


class Subscription(CommonModel):
    title = models.CharField(max_length=150)
    user = models.ForeignKey('users.User', related_name='subscriptions', on_delete=models.CASCADE)
    subgroup = models.ForeignKey(Subgroup, on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False)

    basename = 'subscriptions'

    class Meta:
        unique_together = ('user', 'subgroup')

    def __str__(self):
        return self.title


class Timetable(CommonModel):
    type_of_week = models.SmallIntegerField(choices=TypeWeek.all(), help_text='Тип недели')
    subgroup = models.ForeignKey(Subgroup, on_delete=models.CASCADE)

    basename = 'timetables'
    related_subscription_path = 'subgroup__subscription__'

    class Meta:
        unique_together = ('subgroup', 'type_of_week')

    def __str__(self):
        return f'Расписание для {self.subgroup} группы | {TypeWeek.get_by_value(self.type_of_week)}'

    def get_faculty(self):
        return self.subgroup.group.occupation.faculty.id


class ClassTime(CommonModel):
    number = models.SmallIntegerField()
    start = models.TimeField()
    end = models.TimeField()

    basename = 'class-times'
    related_subscription_path = 'class__timetable__subgroup__subscription__'

    class Meta:
        verbose_name = 'Number of class'
        verbose_name_plural = 'Numbers of classes'

    def __str__(self):
        return f'{self.number}-ая пара'


class Lecturer(CommonModel):
    name = models.CharField(max_length=64)
    patronymic = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)

    basename = 'lecturers'
    related_subscription_path = 'class__timetable__subgroup__subscription__'

    def __str__(self):
        return f'{self.surname} {self.name} {self.patronymic}'


class Class(CommonModel):
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
    type_of_class = models.SmallIntegerField(choices=TYPE_OF_CLASS, help_text='Тип занятия')
    classroom = models.CharField(max_length=10)
    class_time = models.ForeignKey(ClassTime, on_delete=models.PROTECT, help_text='Время начала занятия')
    weekday = models.SmallIntegerField(choices=WEEKDAYS)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.PROTECT)
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)

    basename = 'classes'
    related_subscription_path = 'timetable__subgroup__subscription__'

    class Meta:
        unique_together = ('timetable', 'class_time', 'weekday')
        verbose_name_plural = 'Classes'

    def __str__(self):
        return f'{self.title} | {self.timetable.subgroup} | Timetable ID: {self.timetable.id}'


class UniversityInfo(CommonModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    data = JSONField(default=dict)

    basename = 'university-info'

    class Meta:
        verbose_name_plural = 'University Info'

    def __str__(self):
        return f'University info for {self.content_type.name.capitalize()}'
