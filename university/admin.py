from django.contrib import admin

from .models import Faculty, Occupation, Group, Subgroup, Timetable, ClassTime, Lecturer, Class, UniversityInfo


class SubgroupInline(admin.TabularInline):
    model = Subgroup
    fields = ('id', 'number')
    readonly_fields = ('id',)
    extra = 0


class OccupationInline(admin.TabularInline):
    model = Occupation
    fields = ('id', 'title', 'code')
    readonly_fields = ('id',)
    extra = 0


class ClassInline(admin.TabularInline):
    model = Class
    extra = 0
    fields = (
        'id', 'title', 'type_of_class', 'classroom', 'class_time', 'weekday', 'lecturer', 'state', 'created', 'modified'
    )
    readonly_fields = ('id', 'created', 'modified')
    ordering = ('weekday', 'class_time')


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('title',)
    fields = ('id', 'title')
    readonly_fields = ('id',)
    inlines = (OccupationInline,)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    fields = ('id', 'number')
    readonly_fields = ('id',)
    inlines = (SubgroupInline,)


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    fields = ('id', ('type_of_week', 'state'), 'subgroup', ('created', 'modified'))
    readonly_fields = ('id', 'created', 'modified')
    inlines = (ClassInline,)


@admin.register(ClassTime)
class ClassTimeAdmin(admin.ModelAdmin):
    fields = ('id', 'number', 'start', 'end')
    readonly_fields = ('id',)
    ordering = ('number',)


@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    fields = ('id', ('created', 'modified'), ('name', 'patronymic', 'surname'), 'state')
    readonly_fields = ('id', 'created', 'modified')


@admin.register(UniversityInfo)
class UniversityInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type', 'object_id')
    fields = ('id', 'content_type', 'object_id', 'data', 'state')
    readonly_fields = ('id',)
