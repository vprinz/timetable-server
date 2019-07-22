from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework_swagger.views import get_swagger_view

from common import views
from common.decorators import login_not_required

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),
    url(r'^$', views.home_page),
    url(r'ntf/test/', views.ws_test)
]

schema_view = get_swagger_view(title='Timetable API')
if settings.DEBUG:
    urlpatterns += [
        url(r'^docs/', login_not_required(schema_view))
    ]
