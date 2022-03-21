from django.shortcuts import render


def error404(request, exception):
    return render(request, 'app/error/404.html')

def error400(request, exception):
    return render(request, 'app/error/400.html')

def error403(request, exception):
    return render(request, "app/error/403.html")
