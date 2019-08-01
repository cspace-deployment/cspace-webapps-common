__author__ = 'jblowe'

from django.urls import include, path
from uploadmedia import views

urlpatterns = [
    path('', views.uploadmedia, name='uploadmedia'),
    path('bmu_uploadfiles', views.uploadmedia, name='bmu_uploadfiles'),
    # path('rest/<action>', views.rest, name='rest'),
    path('bmu_checkimagefilenames', views.checkimagefilenames, name='bmu_checkimagefilenames'),
    path('bmu_showqueue', views.showqueue, name='bmu_showqueue'),
    path('bmu_downloadresults/<filename>', views.downloadresults, name='bmu_downloadresults'),
    path('bmu_showresults', views.showresults, name='bmu_showresults'),
    path('bmu_deletejob/<filename>', views.deletejob, name='bmu_deletejob'),
    # path('createmedia', views.createmedia, name='createmedia'),
]
