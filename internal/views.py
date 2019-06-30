__author__ = 'jblowe, amywieliczka'

import time, datetime
from os import path
import logging
#from cspace_django_site.profile import profile

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django import forms
from cspace_django_site.main import cspace_django_site
from common.utils import writeCsv, doSearch, computeStats
from common.utils import setDisplayType, setConstants, loginfo
from common.utils import setupGoogleMap, setupBMapper, computeStats, setupCSV, setupKML, setup4PDF

# from common.utils import CSVPREFIX, CSVEXTENSION
from common.appconfig import loadFields, loadConfiguration
from common import cspace  # we use the config file reading function
from .models import AdditionalInfo

from cspace_django_site import settings

# read common config file
prmz = loadConfiguration('common')
#loginfo('internal','%s :: %s :: %s' % ('internal portal startup', '-', '%s | %s | %s' % (prmz.SOLRSERVER, prmz.IMAGESERVER, prmz.BMAPPERSERVER)), {}, {})

# on startup, setup this webapp layout...
config = cspace.getConfig(path.join(settings.BASE_DIR, 'config'), 'internal')
fielddefinitions = config.get('search', 'FIELDDEFINITIONS')
prmz = loadFields(fielddefinitions, prmz)


def direct(request):
    return redirect('search/')


@login_required()
def search(request):
    if request.method == 'GET' and request.GET != {}:
        context = {'searchValues': request.GET}
        context = doSearch(context, prmz, request)

    else:
        context = setConstants({}, prmz, request)

    loginfo('internal', 'start search', context, request)
    context['additionalInfo'] = AdditionalInfo.objects.filter(live=True)
    return render(request, 'search.html', context)

# @profile("retrieve.prof")
@login_required()
def retrieveResults(request):
    if request.method == 'POST' and request.POST != {}:
        requestObject = request.POST
        form = forms.Form(requestObject)

        if form.is_valid():
            context = {'searchValues': requestObject}
            context = doSearch(context, prmz, request)

            loginfo('internal', 'results.%s' % context['displayType'], context, request)
            return render(request, 'searchResults.html', context)


@login_required()
def bmapper(request):
    if request.method == 'POST' and request.POST != {}:
        requestObject = request.POST
        form = forms.Form(requestObject)

        if form.is_valid():
            context = {'searchValues': requestObject}

            if 'kml' in request.path:
                response = setupKML(request, requestObject, context, prmz)
                loginfo('internal', 'kml', context, request)
                return response
            else:
                context = setupBMapper(request, requestObject, context, prmz)
                loginfo('internal', 'bmapper', context, request)
                return HttpResponse(context['bmapperurl'])

@login_required()
def gmapper(request):
    if request.method == 'POST' and request.POST != {}:
        requestObject = request.POST
        form = forms.Form(requestObject)

        if form.is_valid():
            context = {'searchValues': requestObject}
            context = setupGoogleMap(request, requestObject, context, prmz)

            loginfo('internal', 'gmapper', context, request)
            return render(request, 'maps.html', context)


@login_required()
def dispatch(request):

    if request.method == 'POST' and request.POST != {}:
        requestObject = request.POST
        form = forms.Form(requestObject)

    if 'csv' in request.POST or 'downloadstats' in request.POST:

        if form.is_valid():
            try:
                context = {'searchValues': requestObject}
                csvformat, fieldset, csvitems = setupCSV(request, requestObject, context, prmz)
                loginfo('internal', 'csv', context, request)

                # create the HttpResponse object with the appropriate CSV header.
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="%s-%s.%s"' % (
                    prmz.CSVPREFIX, datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"), prmz.CSVEXTENSION)
                return writeCsv(response, fieldset, csvitems, writeheader=True, csvFormat=csvformat)
            except:
                messages.error(request, 'Problem creating .csv file. Sorry!')
                context['messages'] = messages
                return search(request)

    elif 'pdf' in request.POST:

        if form.is_valid():
            try:
                context = {'searchValues': requestObject}
                loginfo('internal', 'pdf', context, request)
                return setup4PDF(request, context, prmz)

            except:
                messages.error(request, 'Problem creating .pdf file. Sorry!')
                context['messages'] = messages
                return search(request)

    elif 'preview' in request.POST:
        messages.error(request, 'Problem creating print version. Sorry!', request)
        context = {'messages': messages}
        return search(request)

    else:
        messages.error(request, 'Un-implemented action!')
        context = {'messages': messages}
        return search(request)


@login_required()
def statistics(request):
    if request.method == 'POST' and request.POST != {}:
        requestObject = request.POST
        form = forms.Form(requestObject)

        if form.is_valid():
            elapsedtime = time.time()
            try:
                context = {'searchValues': requestObject}
                loginfo('internal', 'statistics1', context, request)
                context = computeStats(request, requestObject, context, prmz)
                loginfo('internal', 'statistics2', context, request)
                context['summarytime'] = '%8.2f' % (time.time() - elapsedtime)
                # 'downloadstats' is handled in writeCSV, via post
                return render(request, 'statsResults.html', context)
            except:
                context['summarytime'] = '%8.2f' % (time.time() - elapsedtime)
                return HttpResponse('Please pick some values!')


def loadNewFields(request, fieldfile, prmx):
    loadFields(fieldfile + '.csv', prmx)

    context = setConstants({}, prmx, request)
    loginfo('internal', 'loaded fields', context, request)
    return render(request, 'search.html', context)
