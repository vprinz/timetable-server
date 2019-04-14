from rest_framework import routers

from django.conf.urls import url, include

from users import views
from university.views import FacultyView

V1 = {
    r'users': views.UserAPIView,
}


def version_urls(version):
    router = routers.DefaultRouter()
    for route, view in version.items():
        base_name = route
        router.register(route, view, base_name)
    return router.urls


urlpatterns = [
    url(r'^(?P<version>[v1]+)/', include(version_urls(V1))),
    url(r'^faculties/$', FacultyView.as_view(), name='faculties')
]
