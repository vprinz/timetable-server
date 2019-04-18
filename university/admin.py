from django.contrib import admin

from .models import Faculty, Occupation, Group, Subgroup, Subscription

admin.site.register(Faculty)
admin.site.register(Occupation)
admin.site.register(Group)
admin.site.register(Subgroup)
admin.site.register(Subscription)
