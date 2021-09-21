from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def about_us(request):
    return render(request, 'about_us.html')


def services(request):
    return render(request, 'services.html')


def contacts(request):
    return render(request, 'contacts.html')