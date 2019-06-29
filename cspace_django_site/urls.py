"""cspace_django_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
#from django.urls import path, include
from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth import views

# admin.autodiscover()

#
# Initialize our web site -things like our AuthN backend need to be initialized.
#
from cspace_django_site.main import cspace_django_site

cspace_django_site.initialize()


urlpatterns = [
    #  Examples:
    #  url(r'^$', 'cspace_django_site.views.home', name='home'),
    #  url(r'^cspace_django_site/', include('cspace_django_site.foo.urls')),

    #  Uncomment the admin/doc line below to enable admin documentation:
    #  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # url(r'^$', 'landing.views.index', name='index'),
    # these are django builtin webapps
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$', views.LoginView, name='login'),
    url(r'^accounts/logout/$', views.LogoutView, name='logout')
]
