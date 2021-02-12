__author__ = 'jblowe'

from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
from django.conf import settings
from os import path
import time

from cspace_django_site.main import cspace_django_site
from common import cspace
from common import appconfig
from common.utils import devicetype

config = cspace_django_site.getConfig()
hostname = cspace.getConfigOptionWithSection(config,
                                             cspace.CONFIGSECTION_AUTHN_CONNECT,
                                             cspace.CSPACE_HOSTNAME_PROPERTY)

TITLE = 'Applications Available'

landingConfig = cspace.getConfig(path.join(settings.BASE_DIR, 'config'), 'landing')
hiddenApps = landingConfig.get('landing', 'hiddenApps').split(',')
publicApps = landingConfig.get('landing', 'publicApps').split(',')


def getapplist(request):
    appList = [app for app in settings.INSTALLED_APPS if not "django" in app and not app in hiddenApps]

    appList = sorted(appList)
    appList = [(app,path.join(settings.WSGI_BASE, app)) for app in appList]
    return appList


def index(request):
    if request.path == '/':
        response = redirect('landing')
        return response
    appList = getapplist(request)
    if not request.user.is_authenticated:
        appList = [app for app in appList if app[0] in publicApps]
    context = {}
    context['version'] = appconfig.getversion()
    context['appList'] = appList
    context['labels'] = 'name file'.split(' ')
    context['apptitle'] = TITLE
    context['hostname'] = hostname
    context['device'] = devicetype(request)
    context['timestamp'] = time.strftime("%b %d %Y %H:%M:%S", time.localtime())

    try:
        alert_config = cspace.getConfig(path.join(settings.BASE_DIR, 'config'), 'alert')
        context['ALERT'] = alert_config.get('alert', 'ALERT')
        context['MESSAGE'] = alert_config.get('alert', 'MESSAGE')
    except:
        context['ALERT'] = ''

    return render(request, 'listApps.html', context)


def applist(request):
    appList = getapplist(request)
    if not request.user.is_authenticated():
        appList = [app for app in appList if app[0] in publicApps]
    return HttpResponse(json.dumps(appList))
