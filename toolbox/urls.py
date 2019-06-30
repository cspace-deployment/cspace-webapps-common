__author__ = 'jblowe'

from django.urls import include, path
from toolbox import views

urlpatterns = [
    path('', views.direct, name='direct'),
    path('<action>', views.toolbox, name='toolbox'),
]
