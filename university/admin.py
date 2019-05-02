from django.contrib import admin

from .models import Faculty, Occupation, Group, Subgroup, Subscription, Timetbale, ClassTime, Lecturer, Class

admin.site.register(Faculty)
admin.site.register(Occupation)
admin.site.register(Group)
admin.site.register(Subgroup)
admin.site.register(Subscription)
admin.site.register(Timetbale)
admin.site.register(ClassTime)
admin.site.register(Lecturer)
admin.site.register(Class)
