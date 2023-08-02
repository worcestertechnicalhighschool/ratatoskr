from django.shortcuts import render


def error404(request, exception):
    return render(request, 'app/errors/404.html')

def error400(request, exception):
    return render(request, 'app/errors/400.html')

def error403(request, exception):
    return render(request, "app/errors/403.html")

def error500(request):
    return render(request, 'app/errors/500.html')
