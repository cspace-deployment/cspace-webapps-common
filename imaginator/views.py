__author__ = 'jblowe'

import os
import re
import time

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from common.utils import doSearch, setConstants, loginfo
from common.appconfig import loadConfiguration, loadFields, getParms
from common import cspace # we use the config file reading function
from cspace_django_site import settings
from os import path
from .models import AdditionalInfo

config = cspace.getConfig(path.join(settings.BASE_DIR, 'config'), 'imaginator')

# read common config file
prmz = loadConfiguration('common')
#loginfo('imaginator', '%s :: %s :: %s' % ('imaginator startup', '-', '%s | %s' % (prmz.SOLRSERVER, prmz.IMAGESERVER)), {}, {})

searchConfig = cspace.getConfig(path.join(settings.BASE_DIR, 'config'), 'imaginator')
prmz.FIELDDEFINITIONS = searchConfig.get('imaginator', 'FIELDDEFINITIONS')

# add in the the field definitions...
prmz = loadFields(prmz.FIELDDEFINITIONS, prmz)

# override a couple parameters for this app
prmz.MAXRESULTS = int(searchConfig.get('imaginator', 'MAXRESULTS'))
prmz.TITLE = searchConfig.get('imaginator', 'TITLE')


def index(request):

    context = setConstants({}, prmz, request)

    if request.method == 'GET':
        context['searchValues'] = request.GET
        prmz.MAXFACETS = 0
        # default display type is Full
        context['displayType'] = 'full'

        if 'keyword' in request.GET:
            context['keyword'] = request.GET['keyword']
        if 'accession' in request.GET:
            context['accession'] = request.GET['accession']
            context['maxresults'] = 1
        if 'submit' in request.GET:
            context['maxresults'] = prmz.MAXRESULTS
            if "Metadata" in request.GET['submit']:
                context['resultType'] = 'metadata'
            elif "Images" in request.GET['submit']:
                context['resultType'] = 'images'
                context['pixonly'] = 'true'
            elif "Lucky" in request.GET['submit']:
                context['resultType'] = 'metadata'
                context['maxresults'] = 1
        else:
            context['resultType'] = 'metadata'

        # do search
        loginfo('imaginator', 'start imaginator search', context, request)
        context = doSearch(context, prmz, request)
        context['additionalInfo'] = AdditionalInfo.objects.filter(live=True)

        return render(request, 'imagineImages.html', context)

    else:
        
        return render(request, 'imagineImages.html', context)
