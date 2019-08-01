from django.urls import include, path
from permalinks import views

urlpatterns = [
    # ex: /objects/9999.99
    # ex: /media/aaaa-aaaa-aaaa-aaaa
    path('<str:itemid>', views.get_item, name='get_item'),
]
