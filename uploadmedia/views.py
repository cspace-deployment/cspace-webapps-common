__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import traceback
#from common.cspace import logged_in_or_basicauth
from django.shortcuts import render, HttpResponse, redirect
from django.core.servers.basehttp import FileWrapper
from os import path, remove
import logging
import time, datetime
from getNumber import getNumber
from utils import SERVERLABEL, SERVERLABELCOLOR, POSTBLOBPATH, INSTITUTION, BATCHPARAMETERS, FIELDS2WRITE, JOBDIR
from utils import getBMUoptions, handle_uploaded_file, assignValue, get_exif, writeCsv
from utils import getJobfile, getJoblist, loginfo, reformat, rendermedia
from specialhandling import specialhandling
from checkBlobs import doChecks

from grouper.grouputils import getfromCSpace

try:
    from xml.etree.ElementTree import tostring, parse, Element, fromstring
except:
    print("could not import with xml.etree.ElementTree")
    raise

# read common config file, just for the version info
from common.appconfig import loadConfiguration
prmz = loadConfiguration('common')

import subprocess
from .models import AdditionalInfo

additionalInfo = AdditionalInfo.objects.filter(live=True)

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)
logger.info('%s :: %s :: %s' % ('uploadmedia startup', '-', '-'))


TITLE = 'Bulk Media Uploader'

override_options = [['ifblank', 'Overide only if blank'],
                    ['always', 'Always Overide']]

overrride_default = 'ifblank'


class im:  # empty class for image metadata
    pass

im.BMUoptions = getBMUoptions()


def setContext(context, elapsedtime):
    # context['status'] = 'up'
    context['additionalInfo'] = additionalInfo
    context['imageserver'] = prmz.IMAGESERVER
    context['cspaceserver'] = prmz.CSPACESERVER
    context['institution'] = prmz.INSTITUTION
    # context['csrecordtype'] = prmz.CSRECORDTYPE
    context['csrecordtype'] = 'media'
    context['apptitle'] = TITLE
    context['version'] = prmz.VERSION
    context['elapsedtime'] = '%8.2f' % elapsedtime
    context['serverlabel'] = SERVERLABEL
    context['serverlabelcolor'] = SERVERLABELCOLOR
    context['dropdowns'] = im.BMUoptions
    context['override_options'] = override_options
    context['timestamp'] = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    return context


def prepareFiles(request, BMUoptions, context):

    validateonly = 'validateonly' in request.POST

    jobnumber = context['jobnumber']
    jobinfo = {}
    images = []
    for lineno, afile in enumerate(request.FILES.getlist('imagefiles')):
        # print afile
        try:
            print "%s %s: %s %s (%s %s)" % ('id', lineno + 1, 'name', afile.name, 'size', afile.size)
            image = get_exif(afile)
            filename, objectnumber, imagenumber, extra = getNumber(afile.name, INSTITUTION)
            datetimedigitized, dummy = assignValue('', 'ifblank', image, 'DateTimeDigitized', {})
            imageinfo = {'id': lineno, 'name': afile.name, 'size': afile.size,
                         'objectnumber': objectnumber,
                         'imagenumber': imagenumber,
                         # 'objectCSID': objectCSID,
                         'date': datetimedigitized,
                         'extra': extra}
            for override in BMUoptions['overrides']:
                dname,refname = assignValue(context[override[2]][0], context[override[2]][1], image, override[3], override[4])
                imageinfo[override[2]] = refname
                # add the Displayname just in case...
                imageinfo['%sDisplayname' % override[2]] = dname

            if not validateonly:
                handle_uploaded_file(afile)

            for option in ['handling', 'approvedforweb']:
                if option in request.POST:
                    imageinfo[option] = request.POST[option]
                else:
                    imageinfo[option] = ''

            if 'handling' in request.POST:
                handling = request.POST['handling']
                for parms in BMUoptions['bmuconstants'][handling]:
                    imageinfo[parms] = BMUoptions['bmuconstants'][handling][parms]

                # special case:
                # borndigital media have their mh id numbers unconditionally replaced with a sequence number
                if imageinfo['handling'] == 'borndigital':
                    # for these, we create a media handling number...
                    # options considered were:
                    # DP-2015-10-08-12-16-43-0001 length: 27
                    # DP-201510081216430001 length: 21
                    # DP-2CBE859E990BFB1 length: 18
                    # DP-2015-10-08-12-16-43-0001 length: 27 the winner! (most legible)
                    mhnumber = jobnumber + ("-%0.4d" % (lineno + 1))
                    #mhnumber = hex(int(mhnumber.replace('-','')))[2:]
                    imageinfo['objectnumber'] = 'DP-' + mhnumber

            specialhandling(imageinfo, context, BMUoptions, INSTITUTION)
            images.append(imageinfo)

        except:
            # raise
            if not validateonly:
                # we still upload the file, anyway...
                try:
                    handle_uploaded_file(afile)
                except:
                    sys.stderr.write("error! file=%s %s" % (afile.name, traceback.format_exc()))

            images.append({'name': afile.name, 'size': afile.size,
                           'error': 'problem uploading file or extracting image metadata, not processed'})

    if len(images) > 0:
        jobinfo['jobnumber'] = jobnumber

        if not validateonly:
            writeCsv(getJobfile(jobnumber) + '.step1.csv', images, FIELDS2WRITE)
        jobinfo['estimatedtime'] = '%8.1f' % (len(images) * 10 / 60.0)

        if 'createmedia' in request.POST:
            jobinfo['status'] = 'createmedia'
            if not validateonly:
                loginfo('start', getJobfile(jobnumber), request)
                try:
                    file_is_OK = True
                    if INSTITUTION == 'cinefiles':
                        # test file content
                        input_file = getJobfile(jobnumber) + '.step1.csv'
                        report_file = getJobfile(jobnumber) + '.check.csv'
                        file_is_OK = doChecks(('', 'file', JOBDIR % '', input_file, report_file))
                        # if ok continue
                        # otherwise ... bail
                        if file_is_OK:
                            pass
                        else:
                            images = []
                            deletejob(request, jobnumber + '.step1.csv')
                            jobinfo['status'] = 'jobfailed'
                            loginfo('process', jobnumber + " QC check failed.", request)
                    if file_is_OK:
                        retcode = subprocess.call([path.join(POSTBLOBPATH, 'postblob.sh'), INSTITUTION, getJobfile(jobnumber), BATCHPARAMETERS])
                        if retcode < 0:
                            loginfo('process', jobnumber + " Child was terminated by signal %s" % -retcode, request)
                        else:
                            loginfo('process', jobnumber + ": Child returned %s" % retcode, request)
                except OSError as e:
                    jobinfo['status'] = 'jobfailed'
                    loginfo('error', "Execution failed: %s" % e, request)
                loginfo('finish', getJobfile(jobnumber), request)

        elif 'uploadmedia' in request.POST:
            jobinfo['status'] = 'uploadmedia'
        else:
            jobinfo['status'] = 'No status possible'

    return jobinfo, images


def setConstants(request, im):

    context = {}

    context['validateonly'] = 'validateonly' in request.POST

    for override in im.BMUoptions['overrides']:
        if override[2] in request.POST:
            context[override[2]] = [request.POST[override[2]],request.POST['override%s' % override[2]]]
        else:
            context[override[2]] = ['', 'never']

    return context


@csrf_exempt
#@logged_in_or_basicauth()
def rest(request, action):
    elapsedtime = time.time()
    status = 'error' # assume murphy's law applies...

    if request.FILES:
        context = setConstants(request, im)
        jobinfo, images = prepareFiles(request, im.BMUoptions, context)
        status = 'ok' # OK, I guess it doesn't after all
    else:
        jobinfo = {}
        images = []
        status = 'no post seen' # OK, I guess it doesn't after all
        return HttpResponse(json.dumps({'status': status}))

    timestamp = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    elapsedtime = time.time() - elapsedtime

    return HttpResponse(json.dumps(
        {'status': status, 'images': images, 'jobinfo': jobinfo, 'elapsedtime': '%8.2f' % elapsedtime}), content_type='text/json')


@login_required()
def uploadfiles(request):
    elapsedtime = time.time()
    context = setConstants(request, im)
    context['jobnumber'] = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

    if request.POST:
        jobinfo, images = prepareFiles(request, im.BMUoptions, context)
    else:
        jobinfo = {}
        images = []

    elapsedtime = time.time() - elapsedtime
    logger.info('%s :: %s :: %s' % ('uploadmedia job ', context['jobnumber'], '-'))
    context = setContext(context, elapsedtime)

    context['jobinfo'] = jobinfo
    context['images'] = images
    context['count'] = len(images)

    return render(request, 'uploadmedia.html', context)


@login_required()
def checkimagefilenames(request):
    elapsedtime = time.time()
    context = setConstants(request, im)
    try:
        filename = request.GET['filename']
        (jobnumber, step, csv ) = filename.split('.')
        context['jobnumber'] = jobnumber
        context['filename'] = filename
        file_handle = open(getJobfile(filename), "rb")
        lines = file_handle.read().splitlines()
        recordtypes = [f.split("|") for f in lines]
        filenames = [ r[0] for r in recordtypes[1:]]
        objectnumbers = []
        seen = {}
        for o in filenames:
            objitems = getNumber(o, INSTITUTION)
            if objitems[1] in seen:
                objectnumbers.append(objitems + (seen[objitems[1]],))
            else:
                asquery = '%s?as=%s_common:%s%%3D%%27%s%%27&wf_deleted=false&pgSz=%s' % ('collectionobjects', 'collectionobjects', 'objectNumber', objitems[1], 10)
                (objecturl, objectx, dummy, itemtime) = getfromCSpace(asquery, request)
                if objectx is None:
                    totalItems = 0
                else:
                    objectx = fromstring(objectx)
                    totalItems = objectx.find('.//totalItems')
                    totalItems = int(totalItems.text)
                #objectcsids = [e.text for e in objectx.findall('.//csid')]
                objectnumbers.append(objitems + (totalItems,))
                seen[objitems[1]] = totalItems
        file_handle.close()
    except:
        raise
        objectnumbers = []
    elapsedtime = time.time() - elapsedtime
    context = setContext(context, elapsedtime)
    context['objectnumbers'] = objectnumbers

    return render(request, 'uploadmedia.html', context)

@login_required()
def downloadresults(request, filename):
    f = open(getJobfile(filename), "rb")
    response = HttpResponse(FileWrapper(f), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


@login_required()
def showresults(request):
    elapsedtime = 0.0
    context = setConstants(request, im)
    try:
        status = request.GET['status']
    except:
        status = 'showfile'
    filename = request.GET['filename']
    context['filename'] = filename
    context['jobstatus'] = request.GET['status']
    f = open(getJobfile(filename), "rb")
    filecontent = f.read()
    if status == 'showmedia':
        context['derivativegrid'] = 'Medium'
        context['sizegrid'] = '240px'
        context['imageserver'] = prmz.IMAGESERVER
        context['items'] = rendermedia(filecontent)
    elif status == 'showinportal':
        pass
    else:
        context['filecontent'] = reformat(filecontent)
    elapsedtime = time.time() - elapsedtime
    context = setContext(context, elapsedtime)

    return render(request, 'uploadmedia.html', context)


@login_required()
def deletejob(request, filename):
    try:
        remove(getJobfile(filename))
        logger.info('%s :: %s' % ('uploadmedia job deleted', filename))

    except:
        logger.info('%s :: %s' % ('uploadmedia tried and failed to delete job', filename))
    return showqueue(request)


@login_required()
def showqueue(request):
    elapsedtime = time.time()
    context = setConstants(request, im)
    jobs, errors, jobcount, errorcount = getJoblist(request)
    if 'checkjobs' in request.POST:
        display_type = 'checkjobs'
    elif 'showerrors' in request.POST:
        display_type = 'showerrors'
    else:
        display_type = None
    context['display'] = display_type
    context['jobs'] = jobs
    context['errors'] = errors
    context['jobcount'] = jobcount
    context['errorcount'] = errorcount
    elapsedtime = time.time() - elapsedtime
    context = setContext(context, elapsedtime)

    return render(request, 'uploadmedia.html', context)