__author__ = 'jblowe'

from django.urls import include, path
from landing import views

urlpatterns = [
               path(r'', views.index, name='index'),
               path(r'applist/', views.applist, name='applist'),
               ]
