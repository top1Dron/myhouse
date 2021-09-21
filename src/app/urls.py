from django.urls import path
from . import views


app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about_us, name='about_us'),
    path('services/', views.services, name="services"),
    path('contact/', views.contacts, name="contacts"),
]
