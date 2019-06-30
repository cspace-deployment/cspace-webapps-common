__author__ = 'remillet,jblowe'
from django.urls import include, path
from service import views

urlpatterns = [
    # ex: /service/intakes
    path('<service>', views.get_list, name='get_list'),
    # ex: /service/intakes/a123-b345-456d
    path('<service>', views.get_item, name='get_item'),
]
