from django.conf.urls import url, include
from rest_framework import routers

from university import views as university
from users import views as users

V1 = {
    r'users': users.UserAPIView,

    r'faculties': university.FacultyAPIView,
    r'occupations': university.OccupationAPIView,
    r'groups': university.GroupAPIView,
    r'subgroups': university.SubgroupAPIView,

    r'university': university.UniversityAPIView,

    r'subscriptions': university.SubscriptionAPIView,
    r'timetables': university.TimetableAPIView,
    r'classes': university.ClassAPIView,
    r'lecturers': university.LectureAPIView,
    r'class-times': university.ClassTimeAPIView,

    r'university-info': university.UniversityInfoAPIView,
}


def version_urls(version):
    router = routers.DefaultRouter()
    for route, view in version.items():
        base_name = route
        router.register(route, view, base_name)
    return router.urls


urlpatterns = [
    url(r'^(?P<version>v1)/', include(version_urls(V1)))
]
