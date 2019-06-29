from django.conf.urls import patterns, url
from permalinks import views

urlpatterns = patterns('',
                       # ex: /objects/9999.99
                       # ex: /media/aaaa-aaaa-aaaa-aaaa
                       url(r'(.*)$', views.get_item, name='get_item'),
                       )
