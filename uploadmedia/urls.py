__author__ = 'jblowe'

from django.urls import include, path
from uploadmedia import views

urlpatterns = [
    path('', views.uploadmedia, name='uploadmedia'),
    path('uploadfiles', views.uploadmedia, name='uploadfiles'),
    path('rest/<action>', views.rest, name='rest'),
    path('checkimagefilenames', views.checkimagefilenames, name='checkimagefilenames'),
    path('showqueue', views.showqueue, name='showqueue'),
    path('downloadresults/<filename>', views.downloadresults, name='downloadresults'),
    path('showresults', views.showresults, name='showresults'),
    path('deletejob/<filename>', views.deletejob, name='deletejob'),
    # path('createmedia', views.createmedia, name='createmedia'),
]
