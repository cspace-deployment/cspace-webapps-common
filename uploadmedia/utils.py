from PIL import Image
from PIL.ExifTags import TAGS
import csv
import codecs
import re
import json
import logging
from os import path, listdir
from os.path import isfile, isdir, join
from xml.sax.saxutils import escape

from common import cspace  # we use the config file reading function
from common.utils import deURN, loginfo
from cspace_django_site import settings

config = cspace.getConfig(path.join(settings.BASE_DIR, 'config'), 'uploadmedia')
TEMPIMAGEDIR = config.get('files', 'directory')
POSTBLOBPATH = config.get('info', 'postblobpath')
BATCHPARAMETERS = config.get('info', 'batchparameters')
BATCHPARAMETERS = BATCHPARAMETERS.replace('.cfg', '')
SERVERLABEL = config.get('info', 'serverlabel')
SERVERLABELCOLOR = config.get('info', 'serverlabelcolor')
INSTITUTION = config.get('info', 'institution')
FIELDS2WRITE = 'name size objectnumber date creator contributor rightsholder imagenumber handling approvedforweb'.split(' ')

if isdir(TEMPIMAGEDIR):
    loginfo('bmu',"Using %s as working directory for images and metadata files" % TEMPIMAGEDIR, {}, {})
else:
    loginfo('bmu',"%s is not an existing directory, using /tmp instead" % TEMPIMAGEDIR, {}, {})
    TEMPIMAGEDIR  = '/tmp'
    # raise Exception("BMU working directory %s does not exist. this webapp will not work without it!" % TEMPIMAGEDIR)

JOBDIR = path.join(TEMPIMAGEDIR, '%s')

# Get an instance of a logger, log some startup info
logger = logging.getLogger(__name__)


def getJobfile(jobnumber):
    return JOBDIR % jobnumber


def jobsummary(jobstats):
    # [ n_imagesuploaded, n_imagesingested, n_errors, [ list of images in error ]
    result = [0, 0, 0, [], 'completed']
    for jobname, status, count, imagefilenames in jobstats:
        if 'pending' in status:
            result[0] = count - 1
            result[4] = 'pending'
        elif 'submitted' in status or 'job started' in status:
            result[0] = count - 1
            inputimages = imagefilenames
        elif 'ingested' in status or 'in progress' in status:
            result[1] = count - 1
            ingestedimages = imagefilenames
        if 'job started' in status or 'in progress' in status:
            result[4] = 'in progress'
    # compute discrepancy, if any
    result[2] = result[0] - result[1]
    if result[2] > 0 and result[4] == 'completed':
        result[4] = 'problem'
    try:
        result[3] = [image for image in inputimages if image not in ingestedimages and image != 'name']
    except:
        pass
    return result


def getJoblist(request):

    if 'num2display' in request.POST:
        num2display = int(request.POST['num2display'])
    else:
        num2display = 50

    jobpath = JOBDIR % ''
    filelist = [f for f in listdir(jobpath) if isfile(join(jobpath, f)) and ('.csv' in f or 'trace.log' in f)]
    jobdict = {}
    errors = []
    filelist = sorted(filelist, reverse=True)
    for f in sorted(filelist, reverse=True):
        if len(jobdict.keys()) > num2display:
            pass
            imagefilenames = []
        else:
            # we only need to count lines if the file is with range...
            linecount, imagefilenames = checkFile(join(jobpath, f))
        parts = f.split('.')
        if 'original' in parts[1]:
            status = 'submitted'
        elif 'processed' in parts[1]:
            status = 'ingested'
        elif 'inprogress' in parts[1]:
            status = 'job started'
        elif 'step1' in parts[1]:
            status = 'pending'
        elif 'step2' in parts[1]:
            continue
        # we are in fact keeping the step2 files for now, but let's not show them...
        # elif 'step2' in parts[1]: status = 'blobs in progress'
        elif 'step3' in parts[1]:
            status = 'media in progress'
        elif 'trace' in parts[1]:
            status = 'run log'
        elif 'check' in parts[1]:
            status = 'check'
        else:
            status = 'unknown'
        jobkey = parts[0]
        if not jobkey in jobdict: jobdict[jobkey] = []
        jobdict[jobkey].append([f, status, linecount, imagefilenames])
    joblist = [[jobkey, True, jobdict[jobkey], jobsummary(jobdict[jobkey])] for jobkey in
               sorted(jobdict.keys(), reverse=True)]
    for ajob in joblist:
        for image in ajob[3][3]:
            errors.append([ajob[0], image])
        for state in ajob[2]:
            if state[1] in ['ingested', 'pending', 'job started']: ajob[1] = False
    num_jobs = len(joblist)
    return joblist[0:num2display], errors, num_jobs, len(errors)


def checkFile(filename):
    file_handle = open(filename)
    # eliminate rows for which an object was not found...
    lines = [l for l in file_handle.read().splitlines() if "not found" not in l]
    images = [f.split("\t")[0] for f in lines]
    images = [f.split("|")[0] for f in images]
    return len(lines), images


def getQueue(jobtypes):
    return [x for x in listdir(JOBDIR % '') if '%s.csv' % jobtypes in x]


def getBMUoptions():
    allowintervention = config.get('info', 'allowintervention')
    allowintervention = True if allowintervention.lower() == 'true' else False

    bmuoptions = []
    bmuconstants = {}

    try:
        usebmuoptions = config.get('info', 'usebmuoptions')
        usebmuoptions = True if usebmuoptions.lower() == 'true' else False
    except:
        usebmuoptions = False

    if usebmuoptions:

        try:
            bmuoptions = config.get('info', 'bmuoptions')
            bmuoptions = json.loads(bmuoptions.replace('\n', ''))
        except:
            loginfo('bmu',"Could not find or could not parse BMU options (parameter 'bmuoptions'), defaults will be taken!", {}, {})
            if bmuoptions: loginfo('',bmuoptions, {}, {})
            bmuoptions = []
        # a dict of dicts...
        try:
            bmuconstants = config.get('info', 'bmuconstants')
            bmuconstants = json.loads(bmuconstants.replace('\n', ''))
        except:
            loginfo('bmu',"Could not find or could not parse BMU constants (parameter 'bmuconstants'), none will be inserted into media records!", {}, {})
            if bmuconstants: loginfo('',bmuconstants, {}, {})
            bmuconstants = {}

        # add the columns for these constants to the list of output values
        for imagetypes in bmuconstants.keys():
            for constants in bmuconstants[imagetypes].keys():
                if not constants in FIELDS2WRITE:
                    FIELDS2WRITE.append(constants)
    else:
        loginfo('bmu',"No BMU options are not enabled. No defaults or special handling of media.", {}, {})

    try:
        overrides = config.get('info', 'overrides')
        overrides = json.loads(overrides.replace('\n', ''))
        for o in overrides:
            loginfo('bmu','BMU will attempt to configure overrides for %s' % o[0], {}, {})
    except:
        loginfo('bmu',"Could not find or could not parse BMU overrides (parameter 'overrides'). Please check your JSON!", {}, {})
        overrides = []

    for override in overrides:
        if not override[2] in FIELDS2WRITE:
            FIELDS2WRITE.append(override[2])

    for override in overrides:
        if override[1] == 'dropdown':
            dropdown = ''
            try:
                dropdown = config.get('info', override[2] + 's')
                dropdown = json.loads(dropdown)
                override.append(dropdown)
                loginfo('bmu','BMU override configured for %ss' % override[2], {}, {})
            except:
                loginfo('bmu','Could not parse overrides for %ss, please check your JSON.' % override[2], {}, {})
                if dropdown: loginfo('bmu',dropdown, {}, {})
        else:
            # add an empty dropdown element -- has to be a dict
            loginfo('bmu','BMU override configured for %s' % override[2], {}, {})
            override.append({})
    return {
        'allowintervention': allowintervention,
        'usebmuoptions': usebmuoptions,
        'bmuoptions': bmuoptions,
        'bmuconstants': bmuconstants,
        'overrides': overrides
    }


# following function taken from stackoverflow and modified...thanks!
def get_exif(fn):
    ret = {}
    if 'image' in fn.content_type:
        i = Image.open(fn)
        try:
            info = i._getexif()
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                ret[decoded] = value
        except:
            pass
    else:
        pass

    return ret


def getCSID(objectnumber):
    # dummy function, for now
    objectCSID = objectnumber
    return objectCSID


def writeCsv(filename, items, writeheader):
    filehandle = codecs.open(filename, 'w', 'utf-8')
    writer = csv.writer(filehandle, delimiter='|')
    writer.writerow(writeheader)
    for item in items:
        row = []
        for x in writeheader:
            if x in item.keys():
                cell = str(item[x])
                cell = cell.strip()
                cell = cell.replace('"', '')
                cell = cell.replace('\n', '')
                cell = cell.replace('\r', '')
            else:
                cell = ''
            row.append(cell)
        writer.writerow(row)
    filehandle.close()


# following function borrowed from Django docs, w modifications
def handle_uploaded_file(f):
    destination = open(path.join(TEMPIMAGEDIR, '%s') % f.name, 'w+')
    with destination:
        for chunk in f.chunks():
            destination.write(chunk)
    destination.close()


def assignValue(defaultValue, override, imageData, exifvalue, refnameList):
    # oh boy! these next couple lines are doozies! sorry!
    if type(refnameList) == type({}):
        refName = refnameList.get(defaultValue, defaultValue)
    else:
        refName = [z[1] for z in refnameList if z[0] == defaultValue]
        # should never happen that there is more than one match, but the configurer may have made a boo-boo
        if len(refName) == 1:
            refName = refName[0]
        else:
            refName = defaultValue
    if override == 'always':
        return defaultValue, refName
    elif exifvalue in imageData:
        imageValue = imageData[exifvalue]
        # a bit of cleanup
        imageValue = imageValue.strip()
        imageValue = imageValue.replace('"', '')
        imageValue = imageValue.replace('\n', '')
        imageValue = imageValue.replace('\r', '')
        imageValue = escape(imageValue)
        return imageValue, refName
    # the follow is really the 'ifblank' condition
    else:
        return defaultValue, refName


# this somewhat desperate function makes an html table from a tab- and newline- delimited string
def reformat(filecontent):
    result = deURN(filecontent)
    result = result.replace('\n','<tr><td>')
    result = result.replace('\t','<td>')
    result = result.replace('|','<td>')
    result = result.replace('False','<span class="error">False</span>')
    result += '</table>'
    return '<table width="100%"><tr><td>\n' + result

# this somewhat desperate function makes an grid display from 'processed' files
def rendermedia(filecontent):
    result = deURN(filecontent)
    rows = result.split('\n')
    FIELDS = rows[0].strip().split('\t')
    rows = rows[1:]
    result = []
    for counter, row in enumerate(rows):
        row = row.strip() # seems there may be a stray \r still at the end of the string.
        if row == '' or row[0] == '#': continue
        row = row.split('\t')
        media = {'otherfields': []}
        media['counter'] = counter
        for i,r in enumerate(row):
            if FIELDS[i] == 'objectnumber':
                media['accession'] = row[i]
            elif FIELDS[i] == 'name':
                media['mainentry'] = row[i]
                # media['otherfields'].append({'label': 'File', 'value': row[i]})
            elif FIELDS[i] == 'objectCSID':
                media['csid'] = row[i]
            elif FIELDS[i] == 'mediaCSID':
                media['media'] = row[i]
            elif FIELDS[i] == 'blobCSID':
                media['blobs'] = [ row[i] ]
            elif FIELDS[i] == 'creator':
                media['otherfields'].append({'label': 'Creator', 'value': row[i]})
            elif FIELDS[i] == 'description':
                media['otherfields'].append({'label': 'Description', 'value': row[i]})
            elif FIELDS[i] == 'date':
                media['otherfields'].append({'label': 'Image Date', 'value': row[i]})
        result.append(media)
    return result
