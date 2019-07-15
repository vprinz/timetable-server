from django.conf.urls import url, include
from django.contrib import admin

from common import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),
    url(r'^$', views.home_page),
    url(r'ntf/test/', views.ws_test)
]
