__author__ = 'jblowe'

# from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from common import cspace # we use the config file reading function
from common.utils import loginfo
from cspace_django_site import settings

from os import path
import urllib
import time
import logging
import base64
import re

config = cspace.getConfig(path.join(settings.BASE_DIR, 'config'), 'imageserver')
username = config.get('connect', 'username')
password = config.get('connect', 'password')
hostname = config.get('connect', 'hostname')
realm = config.get('connect', 'realm')
protocol = config.get('connect', 'protocol')
port = config.get('connect', 'port')
port = ':%s' % port if port else ''

server = protocol + "://" + hostname + port

# see if watermarking is enabled
try:
    watermark = config.get('info', 'watermark')
    watermark = True if (watermark.lower() in 'true yes on') else False
    watermark_image = config.get('info', 'watermarkimage')
    watermark_transparency = float(config.get('info', 'watermarktransparency'))
    if watermark_transparency > 1.0 or watermark_transparency < 0.0:
        raise Exception('watermarktransparency value is invalid: %s' % watermark_transparency)
    watermark_percent = float(config.get('info', 'watermarkpercent'))
    if watermark_percent > 1.0 or watermark_percent < 0.0:
        raise Exception('watermarkpercent value is invalid: %s' % watermark_percent)
    if not path.isfile(watermark_image):
        raise Exception('could not find watermark image: %s' % watermark_image)
    loginfo('imageserver', 'watermarking enabled. transparency: %s, image: %s' % (watermark_transparency, watermark_image), {}, {})
except Exception as inst:
    watermark = False

    loginfo('imageserver', inst.args[0], {}, {})
    loginfo('imageserver', '%s' % 'configuration problem. watermarking NOT enabled.', {}, {})

imageunavailable = config.get('info', 'imageunavailable')
unavailable_mime_type = 'jpg'

try:
    unavailable_mime_type = re.search(r'^.*?\.(.*)', imageunavailable).group(1)
    if unavailable_mime_type.lower() == 'svg':
        unavailable_mime_type = 'svg+xml'
except:
    loginfo('imageserver','could not extract MIME-type for 404 image: %s; assuming "jpg"' % imageunavailable, {}, {})

try:
    derivatives_served = config.get('info', 'derivatives_served')
    derivatives_served = derivatives_served.split(',')
    loginfo('imageserver','Derivatives served: %s' % derivatives_served, {}, {})
except:
    loginfo('imageserver','No derivatives are restricted', {}, {})
    derivatives_served = None

# loosely based on https://stackoverflow.com/questions/32034160/creating-a-watermark-in-python
from wand.image import Image


def add_watermark(image1, image2):
    with Image(blob=image1) as background:
        with Image(filename=image2) as watermark:
            background_size = background.size
            watermark_size = watermark.size
            # (width, height): is the width bigger than the height?
            if background_size[0] > background_size[1]:
                background_to_watermark_ratio = float(background_size[0]) / watermark_size[0]
            else:
                background_to_watermark_ratio = float(background_size[1]) / watermark_size[1]
            watermark.transform(resize='%s%%' % int(100.0 * background_to_watermark_ratio * watermark_percent))
            background.watermark(image=watermark, transparency=watermark_transparency)
            return background.make_blob()


# @login_required()
def get_image(request, image):
    elapsedtime = time.time()
    try:
        # if the user is authenticated, they can see anything.
        # otherwise, they see only what the imageserver is configured to let them see.
        if not request.user.is_authenticated():
            image_ok = False
            # if no list of authorized derivatives is set in the config file, all are available
            if not derivatives_served:
                image_ok = True
            # otherwise if a list was specified, check to see if we can serve this derivative
            else:
                for derivative in derivatives_served:
                    if derivative in image:
                        image_ok = True
                        break
            if not image_ok:
                html = '''
            <div style="height: 90px; width: 96px; background-color: lightgray; font-size: 80%;">
            <br/>&nbsp;[not authorized]
            </div>'''
                return HttpResponse(html, content_type='text/html')

        passman = urllib.request.HTTPPasswordMgr()
        passman.add_password(realm, server, username, password)
        authhandler = urllib.request.HTTPBasicAuthHandler(passman)
        opener = urllib.request.build_opener(authhandler)

        unencoded_credentials = "%s:%s" % (username, password)
        auth_value = 'Basic %s' % base64.b64encode(unencoded_credentials).strip()
        opener.addheaders = [('Authorization', auth_value)]
        urllib.request.install_opener(opener)
        url = "%s/cspace-services/%s" % (server, image)
        f = urllib.request.urlopen(url)

        msg = 'image'
        data = f.read()
        headers = f.info()
        content_type = headers.type
        content_disposition = ''
        for h in headers.headers:
            if 'Content-Disposition' in h:
                content_disposition = h
                break
        try:
            extractfilename = re.search('filename="(.*)"',content_disposition)
            filename = extractfilename.group(1)
        except:
            filename = ''

    except:
        msg = 'image error'
        data = open(path.join(settings.STATIC_ROOT, 'cspace_django_site/images', imageunavailable), 'r').read()
        content_type = 'image/%s' % unavailable_mime_type
        filename = imageunavailable

    if watermark:
        try:
            data = add_watermark(data, watermark_image)
        except:
            raise
            loginfo('imageserver', '%s :: %s :: %s' % ('watermark failed', '-', url), {}, {})
    elapsedtime = time.time() - elapsedtime
    loginfo('imageserver', '%s :: %s :: %s' % (msg, '-', '%s :: %8.3f seconds' % (image, elapsedtime)), {}, {})
    response = HttpResponse(data, content_type=content_type)
    response['Content-Disposition'] = 'filename="%s"' % filename
    return response
