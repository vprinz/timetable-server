from django.conf.urls import url, include
from django.contrib import admin

from common.decorators import login_not_required
from common.views import HomeView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),
    url(r'^$', login_not_required(HomeView.as_view()))
]
