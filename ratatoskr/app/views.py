from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'app/pages/index.html', {})

def create_schedule(request):
    if request.method == "POST":
        pass
    return render(request, 'app/pages/create_schedule.html', {})
