from django.conf.urls import url, include
from rest_framework import routers

from university import views as university_v1
from users import views as users

V1 = {
    r'users': users.UserAPIView,

    r'faculties': university_v1.FacultyAPIView,
    r'occupations': university_v1.OccupationAPIView,
    r'groups': university_v1.GroupAPIView,
    r'subgroups': university_v1.SubgroupAPIView,

    r'university': university_v1.UniversityAPIView,

    r'subscriptions': university_v1.SubscriptionAPIView,
    r'timetables': university_v1.TimetableAPIView,
    r'classes': university_v1.ClassAPIView,
    r'lecturers': university_v1.LectureAPIView,
    r'class-times': university_v1.ClassTimeAPIView,

    r'university-info': university_v1.UniversityInfoAPIView,
}


def version_urls(version):
    router = routers.DefaultRouter()
    for route, view in version.items():
        base_name = route
        router.register(route, view, base_name)
    return router.urls


urlpatterns = [
    url(r'^(?P<version>v1)/', include(version_urls(V1))),
]
