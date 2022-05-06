__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import traceback
import urllib.parse
#from common.cspace import logged_in_or_basicauth
from django.shortcuts import render, HttpResponse, redirect

from PIL import Image

from os import path, remove
import time
from uploadmedia.getNumber import getNumber
from uploadmedia.utils import SERVERLABEL, SERVERLABELCOLOR, POSTBLOBPATH, INSTITUTION, BATCHPARAMETERS, FIELDS2WRITE, JOBDIR
from uploadmedia.utils import getBMUoptions, handle_uploaded_file, assignValue, get_exif, writeCsv
from uploadmedia.utils import getJobfile, getJoblist, reformat, rendermedia
from uploadmedia.specialhandling import specialhandling
from uploadmedia.checkBlobs import doChecks
from common.utils import loginfo

from grouper.grouputils import getfromCSpace

from xml.etree.ElementTree import fromstring

# read common config file, just for the version info
from common.appconfig import loadConfiguration
prmz = loadConfiguration('common')

import subprocess
from .models import AdditionalInfo

additionalInfo = AdditionalInfo.objects.filter(live=True)

loginfo('bmu startup', '-', {}, {})

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

    jobnumber = context['jobnumber']
    jobinfo = {}
    images = []
    for lineno, afile in enumerate(request.FILES.getlist('imagefiles')):
        try:
            loginfo('bmu', ("%s %s: %s %s (%s %s)" % ('id', lineno + 1, 'name', afile.name, 'size', afile.size)), context, request)
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
            raise
            # we still upload the file, anyway...
            try:
                handle_uploaded_file(afile)
            except:
                sys.stderr.write("error! file=%s %s" % (afile.name, traceback.format_exc()))

            images.append({'name': afile.name, 'size': afile.size,
                           'error': 'problem uploading file or extracting image metadata, not processed'})

    if len(images) > 0:
        jobinfo['jobnumber'] = jobnumber

        writeCsv(getJobfile(jobnumber) + '.step1.csv', images, FIELDS2WRITE)
        jobinfo['estimatedtime'] = '%8.1f' % (len(images) * 10 / 60.0)

        if 'createmedia' in request.POST:
            jobinfo['status'] = 'createmedia'
            jobinfo['status'] = runjob(jobnumber, context, request)

        elif 'uploadmedia' in request.POST:
            jobinfo['status'] = 'uploadmedia'
        else:
            jobinfo['status'] = 'No status possible'

    return jobinfo, images


def setConstants(request, im):

    context = {}

    for override in im.BMUoptions['overrides']:
        if override[2] in request.POST:
            context[override[2]] = [request.POST[override[2]],request.POST['override%s' % override[2]]]
        else:
            context[override[2]] = ['', 'never']

    return context


def runjob(jobnumber, context, request):
    loginfo('bmu online job submission started', getJobfile(jobnumber), context, request)
    status = 'jobstarted'
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
                deletejob(request, jobnumber + '.step1.csv')
                loginfo('bmu ERROR:  process', jobnumber + " QC check failed.", context, request)
                status = 'jobfailed'
        if file_is_OK:
            p_object = subprocess.Popen([path.join(POSTBLOBPATH, 'postblob.sh'), INSTITUTION, getJobfile(jobnumber), BATCHPARAMETERS])
            pid = ''
            if p_object._child_created:
                pid = p_object.pid
                loginfo('bmu online job submitted:', jobnumber + f': Child returned {p_object.returncode}, pid {pid}', context, request)
            else:
                loginfo('bmu ERROR:', jobnumber + f': Child returned {p_object.returncode}, pid {pid}', context, request)
    except OSError as e:
        loginfo('error', "ERROR: Execution failed: %s" % e, context, request)
        status = 'jobfailed'
    loginfo('bmu online submission finished', getJobfile(jobnumber), context, request)
    return status


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
def uploadmedia(request):
    elapsedtime = time.time()
    context = setConstants(request, im)
    context['jobnumber'] = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

    if request.POST:
        jobinfo, images = prepareFiles(request, im.BMUoptions, context)
    else:
        jobinfo = {}
        images = []

    elapsedtime = time.time() - elapsedtime
    loginfo('bmu', '%s :: %s' % ('uploadmedia job ', context['jobnumber']), {}, request)
    context = setContext(context, elapsedtime)

    context['jobinfo'] = jobinfo
    context['images'] = images
    context['count'] = len(images)
    context['url_institution'] = context['institution'].replace('botgarden', 'ucbg')

    return render(request, 'uploadmedia.html', context)


def checkOrientation(image_file):
    try:
        image = Image.open(image_file)
        image_size = image.size
        if image_size[0] < image_size[1]:
                return 'Portrait'
        return 'Landscape'
    except:
        return 'Could not tell'


@login_required()
def checkimagefilenames(request):
    elapsedtime = time.time()
    context = setConstants(request, im)
    try:
        filename = request.GET['filename']
        (jobnumber, step, csv ) = filename.split('.')
        context['jobnumber'] = jobnumber
        context['filename'] = filename
        file_handle = open(getJobfile(filename), 'r')
        lines = file_handle.read().splitlines()
        # TODO the delimiters used should be rationalized someday
        if '|' in lines[0]:
            delim = '|'
        else:
            delim = '\t'
        recordtypes = [tuple(list(f.split(delim)[i] for i in [0, 2, 7, 8])) for f in lines]
        seen = {}
        checked_objects = []
        for objitems in recordtypes[1:]:
            asquery = '%s?as=%s_common:%s%%3D%%27%s%%27&wf_deleted=false&pgSz=%s' % ('collectionobjects', 'collectionobjects', 'objectNumber', urllib.parse.quote_plus(objitems[1]), 10)
            (objecturl, objectx, dummy, itemtime) = getfromCSpace(asquery, request)
            if objectx is None:
                totalItems = 0
            else:
                objectx = fromstring(objectx)
                totalItems = objectx.find('.//totalItems')
                totalItems = int(totalItems.text)
                try:
                    csid = objectx.find('.//csid').text
                    csidquery = f'media?rtObj={csid}'
                    (objecturl, objectx, dummy, itemtime) = getfromCSpace(csidquery, request)
                    objectx = fromstring(objectx)
                    media = [m.text for m in objectx.findall('.//csid')]
                except:
                    csid = ''
                    media = []
            media_file = getJobfile(objitems[0])
            orientation = checkOrientation(media_file)
            payload = objitems + upload_type_check(totalItems, objitems) + (media, orientation)
            checked_objects.append(payload)
            seen[objitems[1]] = payload
        file_handle.close()
    except:
        raise
        checked_objects = []
    elapsedtime = time.time() - elapsedtime
    context = setContext(context, elapsedtime)
    context['objectnumbers'] = checked_objects
    context['url_institution'] = context['institution'].replace('botgarden', 'ucbg')

    return render(request, 'uploadmedia.html', context)

def upload_type_check(num_items, objitem):
    handling = objitem[3]
    if num_items == 0:
        return (num_items, 'Not found')
    if num_items > 1:
        return (num_items, f'Duplicated {num_items} times!')
    else:
        return (num_items, 'Found')

@login_required()
def downloadresults(request, filename):
    f = open(getJobfile(filename), 'r')
    response = HttpResponse(f, content_type='text/csv')
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
    f = open(getJobfile(filename), 'r')
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
    context['url_institution'] = context['institution'].replace('botgarden', 'ucbg')

    return render(request, 'uploadmedia.html', context)


@login_required()
def startjob(request, filename):
    try:
        context = setConstants(request, im)
        (jobnumber, step, csv ) = filename.split('.')
        context['jobnumber'] = jobnumber
        context['filename'] = filename
        runjob(jobnumber, context, request)
        # give the job a chance to start to ensure the queue listing is updated properly.
        time.sleep(1)
        loginfo('bmu', '%s :: %s' % ('uploadmedia online job submission requested', filename), {}, {})
    except:
        loginfo('bmu', '%s :: %s' % ('ERROR: uploadmedia tried and failed to start job', filename), {}, {})
    return redirect('../bmu_showqueue')


@login_required()
def deletejob(request, filename):
    try:
        remove(getJobfile(filename))
        loginfo('bmu', '%s :: %s' % ('uploadmedia job deleted', filename), {}, {})
    except:
        loginfo('bmu', '%s :: %s' % ('ERROR: uploadmedia tried and failed to delete job', filename), {}, {})
    return redirect('../bmu_showqueue')


@login_required()
def showqueue(request):
    elapsedtime = time.time()
    context = setConstants(request, im)
    jobs, errors, jobcount, errorcount = getJoblist(request)
    if 'showerrors' in request.POST:
        display_type = 'showerrors'
    else:
        display_type = 'checkjobs'
    context['display'] = display_type
    context['jobs'] = jobs
    context['errors'] = errors
    context['jobcount'] = jobcount
    context['errorcount'] = errorcount
    elapsedtime = time.time() - elapsedtime
    context = setContext(context, elapsedtime)
    context['url_institution'] = context['institution'].replace('botgarden', 'ucbg')

    return render(request, 'uploadmedia.html', context)
