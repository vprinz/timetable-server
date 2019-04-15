from rest_framework import routers

from django.conf.urls import url, include

from users import views as users
from university import views as university

V1 = {
    r'users': users.UserAPIView,
    r'university': university.FacultyAPIView,
}


def version_urls(version):
    router = routers.DefaultRouter()
    for route, view in version.items():
        base_name = route
        router.register(route, view, base_name)
    return router.urls


urlpatterns = [
    url(r'^(?P<version>[v1]+)/', include(version_urls(V1)))
]
