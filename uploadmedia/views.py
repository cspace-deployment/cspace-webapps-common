__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import traceback
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
    checked_images = []
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

            checked_images.append(handle_uploaded_file(afile, request))

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
            try:
                images.append({'name': afile.name, 'size': afile.size,
                               'error': 'problem uploading file or extracting image metadata, this file will be skipped'})
            except:
                sys.stderr.write("error! file=%s %s" % (afile.name, traceback.format_exc()))


    if len(images) > 0:
        jobinfo['jobnumber'] = jobnumber

        writeCsv(getJobfile(jobnumber) + '.step1.csv', images, FIELDS2WRITE)
        writeCsv(getJobfile(jobnumber) + '.check.csv', checked_images, 'objectnumber,filename,items,status,media count,orientation,media csids'.split(','))
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
            file_is_OK = doChecks(('', 's3', JOBDIR % '', input_file, report_file))
            # if ok continue
            # otherwise ... bail
            if file_is_OK:
                pass
            else:
                deletejob(request, jobnumber + '.step1.csv')
                loginfo('bmu ERROR:  process', jobnumber + " QC check failed.", context, request)
                status = 'jobfailed'
        if file_is_OK:
            # start a bmu job asynchronously. do not wait for job to finish before returning to user
            # process will terminate when job finishes.
            # TODO: figure out how to 'fire and forget' this batch job so it does nat make zombies
            p_object = subprocess.Popen([path.join(POSTBLOBPATH, 'postblob.sh'), INSTITUTION, getJobfile(jobnumber), BATCHPARAMETERS])
            time.sleep(1)
            if p_object._child_created:
                loginfo('bmu online job submitted:', jobnumber + f': Child returned {p_object.returncode}', context, request)
            else:
                loginfo('bmu ERROR:', jobnumber + f': Child returned {p_object.returncode}', context, request)
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


@login_required()
def downloadresults(request, filename):
    f = open(getJobfile(filename), mode="r", encoding="utf-8")
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
    f = open(getJobfile(filename), mode="r", encoding="utf-8")
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
        loginfo('bmu', '%s :: %s' % ('uploadmedia online job submission requested', filename), {}, {})
        runjob(jobnumber, context, request)
        # give the job a chance to start to ensure the queue listing is updated properly.
        time.sleep(1)
    except:
        loginfo('bmu', '%s :: %s' % ('ERROR: uploadmedia tried and failed to start job', filename), {}, {})
    return redirect('../bmu_showqueue')


@login_required()
def deletejob(request, filename):
    try:
        remove(getJobfile(filename))
        remove(getJobfile(filename.replace('step1','check')))
        loginfo('bmu', '%s :: %s' % ('pending uploadmedia job deleted', filename), {}, {})
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
