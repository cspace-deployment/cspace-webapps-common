__author__ = 'jblowe'

from django.urls import include, path
from suggestpostgres import views

urlpatterns = [
    # ex: /suggestpostgres?q=ASPARAG&elementID=ta.taxon
    path('', views.postgresrequest, name='postgresrequest'),
]
