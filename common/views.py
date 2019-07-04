from django.shortcuts import render

from common.decorators import login_not_required


@login_not_required
def home_page(request):
    return render(request, 'home.html')


@login_not_required
def ws_test(request):
    return render(request, 'ws_test.html')
