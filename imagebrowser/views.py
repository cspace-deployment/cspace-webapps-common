__author__ = 'jblowe'

import os
import re
import time
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response

from common.utils import doSearch, setConstants, loginfo
from common.appconfig import loadConfiguration, loadFields, getParms
from common import cspace
from cspace_django_site import settings
from os import path
from .models import AdditionalInfo

loginfo('imagebrowser', 'imagebrowser startup', {}, {})

# read common config file
common = 'common'
prmz = loadConfiguration(common)
loginfo('imagebrowser','Configuration for %s successfully read' % common, {}, {})

searchConfig = cspace.getConfig(path.join(settings.BASE_DIR, 'config'), 'imagebrowser')
prmz.FIELDDEFINITIONS = searchConfig.get('imagebrowser', 'FIELDDEFINITIONS')

# add in the the field definitions...
prmz = loadFields(prmz.FIELDDEFINITIONS, prmz)

# override these two values if they were set above
prmz.MAXRESULTS = int(searchConfig.get('imagebrowser', 'MAXRESULTS'))
prmz.TITLE = searchConfig.get('imagebrowser', 'TITLE')

# @login_required()
def images(request):

    context = setConstants({}, prmz, request)

    if request.method == 'GET' and request.GET != {}:
        context['searchValues'] = request.GET
        prmz.MAXFACETS = 0

        if 'keyword' in request.GET:
            context['keyword'] = request.GET['keyword']
        if 'accession' in request.GET:
            context['accession'] = request.GET['accession']
            context['maxresults'] = 1

        context['maxresults'] = prmz.MAXRESULTS
        # use the grid display fields (we only show two of the required ones)
        context['displayType'] = 'grid'
        # it's an image browser, so only return items with images...
        context['pixonly'] = 'true'

        # do search
        loginfo('imagebrowser', 'start imagebrowser search', context, request)
        context = doSearch(context, prmz, request)
        context['additionalInfo'] = AdditionalInfo.objects.filter(live=True)

        return render(request, 'showImages.html', context)

    else:

        context = setConstants({}, prmz, request)
        context['pgNum'] = 10
        context['maxresults'] = 20
        return render(request, 'showImages.html', context)
