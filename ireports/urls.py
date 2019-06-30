__author__ = 'jblowe'

from django.urls import include, path
from ireports import views

urlpatterns = [
    path('', views.index, name='ireports'),
    path('<report_csid>', views.ireport, name='ireport'),
]
