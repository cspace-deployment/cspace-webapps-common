__author__ = 'remillet,jblowe'
from django.urls import include, path
from service import views

urlpatterns = [
    # ex: /service/intakes
    path('(?P<service>[\w-]+)/', views.get_list, name='get_list'),
    # ex: /service/intakes/a123-b345-456d
    path('(?P<service>[\w-]+)/(?P<item_csid>[\w-]+)/', views.get_item, name='get_item'),
]
