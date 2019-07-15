from django.conf import settings
from django.shortcuts import render

from common.decorators import login_not_required


@login_not_required
def home_page(request):
    return render(request, 'home.html')


@login_not_required
def ws_test(request):
    host = settings.SERVER_FULL_URL.split(':')[0]
    port = 8000 if settings.DEPLOYMENT_NAME == 'local' else 8001
    return render(request, 'ws_test.html', {'ws_url': f'ws:{host}:{port}/notifications/'})
