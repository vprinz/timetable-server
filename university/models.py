from django.db import models


class Faculty(models.Model):
    title = models.CharField(max_length=256, unique=True)
    short_title = models.CharField(max_length=16, unique=True, null=True, help_text='Сокращённое название факультета.')
    occupations = models.ManyToManyField('university.Occupation', blank=True)

    class Meta:
        verbose_name = 'Факультет'
        verbose_name_plural = 'Факультеты'

    def __str__(self):
        return self.short_title


class Occupation(models.Model):
    title = models.CharField(max_length=256, unique=True)
    short_title = models.CharField(max_length=16, unique=True, null=True, help_text='Сокращённое название направления.')
    code = models.CharField(max_length=10, unique=True)
    groups = models.ManyToManyField('university.Group', blank=True)

    class Meta:
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'

    def __str__(self):
        return f'{self.short_title} {self.code}'


class Group(models.Model):
    title = models.CharField(max_length=2, primary_key=True)

    def __str__(self):
        return self.title
