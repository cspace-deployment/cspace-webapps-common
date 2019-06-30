__author__ = 'jblowe'

from django.urls import include, path
from imagebrowser import views

urlpatterns = [
    path('', views.images, name='images'),
    path('(?P<count>[\d]+)/', views.images, name='images'),
]
