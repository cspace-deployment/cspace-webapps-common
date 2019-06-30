__author__ = 'jblowe'

from django.urls import include, path
from imaginator import views

urlpatterns = [
    path('', views.index, name='index'),
]
