__author__ = 'jblowe'

from django.urls import include, path
from suggestsolr import views

urlpatterns = [
    # ex: /suggestsolr?q=ASPARAG&elementID=family
    path('', views.solrrequest, name='solrrequest'),
]
