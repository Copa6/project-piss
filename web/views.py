from django.shortcuts import render

# Create your views here.

app_name = "web"


def index(request):
    return render(request, 'web/index.html', {})