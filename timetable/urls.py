from django.conf.urls import url, include
from django.contrib import admin

from common import views

urlpatterns = [
    url(r'^$', views.home_page),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls'))
]
