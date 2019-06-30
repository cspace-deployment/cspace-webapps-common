__author__ = 'amywieliczka, jblowe'

from django.urls import include, path
from search import views

urlpatterns = [
    path('', views.direct, name='direct'),
    path('search/', views.search, name='search'),
    path('search/(?P<fieldfile>[\w-]+)', views.loadNewFields, name='loadNewFields'),
    path('results/', views.retrieveResults, name='retrieveResults'),
    path('json/', views.retrieveJSON, name='retrieveJSON'),
    path('json/facet/', views.facetJSON, name='facetJSON'),
    path('json-entry/', views.JSONentry, name='JSONentry'),
    path('bmapper/', views.bmapper, name='bmapper'),
    path('statistics/', views.statistics, name='statistics'),
    path('dispatch/', views.dispatch, name='dispatch'),
    # path('csv/', views.csv, name='csv'),
    # path('pdf/', views.pdf, name='pdf'),
    path('gmapper/', views.gmapper, name='gmapper'),
]
