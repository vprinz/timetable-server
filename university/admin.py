from django.contrib import admin

from .models import Faculty, Occupation, Group, Subgroup, Timetbale, ClassTime, Lecturer, Class, UniversityInfo


class SubgroupInline(admin.TabularInline):
    model = Subgroup
    extra = 0


class OccupationInline(admin.TabularInline):
    model = Occupation
    extra = 0


class ClassInline(admin.TabularInline):
    model = Class
    extra = 0
    fields = ('title', 'type_of_class', 'classroom', 'class_time', 'weekday', 'lecturer', 'created', 'modified')
    readonly_fields = ('created', 'modified')
    ordering = ('weekday', 'class_time')


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    fields = ('title', 'current_type_of_week')
    inlines = (OccupationInline,)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    inlines = (SubgroupInline,)


@admin.register(Timetbale)
class TimetableAdmin(admin.ModelAdmin):
    fields = ('type_of_week', 'subgroup', ('created', 'modified'))
    readonly_fields = ('created', 'modified')
    inlines = (ClassInline,)


@admin.register(ClassTime)
class ClassTimeAdmin(admin.ModelAdmin):
    pass


@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    pass


@admin.register(UniversityInfo)
class UniversityInfoAdmin(admin.ModelAdmin):
    pass
