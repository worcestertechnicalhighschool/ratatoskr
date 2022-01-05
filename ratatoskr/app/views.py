from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

# Create your views here.
def index(request):
    return render(request, 'app/pages/index.html', {})

def create_schedule(request):
    if not request.user.is_authenticated:
        raise PermissionDenied()
    if request.method == "POST":
        request.post
    return render(request, 'app/pages/create_schedule.html', {})
