__author__ = 'jblowe'

from django.urls import include, path
from ireports import views

urlpatterns = [
    path('', views.index, name='index'),
    path('(?P<report_csid>[\w-]+)/', views.ireport, name='report'),
]
