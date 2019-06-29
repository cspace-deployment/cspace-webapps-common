__author__ = 'jblowe'

from django.conf.urls import patterns, url
from uploadmedia import views

urlpatterns = patterns('',
                       url(r'^/?$', views.uploadfiles),
                       url(r'^uploadfiles', views.uploadfiles, name='uploadfiles'),
                       url(r'^rest/(?P<action>[\w\-\.]+)$', views.rest, name='rest'),
                       url(r'^checkimagefilenames', views.checkimagefilenames, name='checkimagefilenames'),
                       url(r'^showqueue', views.showqueue, name='showqueue'),
                       url(r'^downloadresults/(?P<filename>[\w\-\.]+)$', views.downloadresults, name='downloadresults'),
                       url(r'^showresults', views.showresults, name='showresults'),
                       url(r'^deletejob/(?P<filename>[\w\-\.]+)?$', views.deletejob, name='deletejob'),
                       #url(r'createmedia', views.createmedia, name='createmedia'),
                       )
