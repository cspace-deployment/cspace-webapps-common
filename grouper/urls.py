__author__ = 'jblowe'

from django.urls import include, path
from grouper import views

urlpatterns = [
    path('', views.index, name='grouper'),
]
