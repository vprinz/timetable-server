from django.conf.urls import url, include
from django.contrib import admin

from common.views import home_page, ws_test

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),
    url(r'^$', home_page),
    url(r'test/', ws_test)
]
