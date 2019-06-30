__author__ = 'jblowe'

from django.urls import include, path
from imagebrowser import views

urlpatterns = [
    path('', views.images, name='images'),
    path('<count>', views.images, name='images'),
]
