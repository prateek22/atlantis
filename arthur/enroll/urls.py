from django.urls import path

from . import views

app_name = 'edr'

urlpatterns = [
    path('', views.index, name='index'),
    path('enroll', views.enroll, name='enroll'),
]