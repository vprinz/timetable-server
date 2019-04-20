from django.db import models


class Faculty(models.Model):
    title = models.CharField(max_length=256, unique=True)
    short_title = models.CharField(max_length=16, unique=True, null=True, help_text='Сокращённое название факультета.')

    class Meta:
        verbose_name = 'Факультет'
        verbose_name_plural = 'Факультеты'

    def __str__(self):
        return self.short_title


class Occupation(models.Model):
    title = models.CharField(max_length=256, unique=True)
    short_title = models.CharField(max_length=16, unique=True, null=True, help_text='Сокращённое название направления.')
    code = models.CharField(max_length=10, unique=True)
    faculty = models.ForeignKey(Faculty, related_name='occupations', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'

    def __str__(self):
        return f'{self.short_title} {self.code}'


class Group(models.Model):
    number = models.CharField(max_length=2, primary_key=True)
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
    name = models.CharField(max_length=150, null=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    subgroup = models.ForeignKey(Subgroup, on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'subgroup')
