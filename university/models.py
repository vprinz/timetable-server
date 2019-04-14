from django.db import models


class Faculty(models.Model):
    title = models.CharField(max_length=256, unique=True)


class Occupation(models.Model):
    title = models.CharField(max_length=256, unique=True)
    code = models.CharField(max_length=10, unique=True)


class Group(models.Model):
    title = models.CharField(max_length=2, primary_key=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    occupation = models.ForeignKey(Occupation, on_delete=models.CASCADE)
