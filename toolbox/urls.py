__author__ = 'jblowe'

from django.urls import include, path
from toolbox import views

urlpatterns = [
    path('', views.index, name='index'),
    path('(?P<action>[\w\-\.]+)', views.toolbox, name='toolbox'),
]
