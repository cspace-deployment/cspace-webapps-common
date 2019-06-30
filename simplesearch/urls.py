__author__ = 'jblowe'

from django.urls import include, path
from simplesearch import views

urlpatterns = [
    path('', views.simplesearch, name='simplesearch'),
]
