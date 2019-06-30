__author__ = 'jblowe'

from django.urls import include, path
from suggest import views

urlpatterns = [
    # ex: /suggest?q=ASPARAG&elementID=family&source=solr
    path('', views.suggest, name='suggest'),
]
