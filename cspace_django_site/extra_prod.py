import os

# settings needed for Production

try:
    # get the tracking id for Prod
    from trackingids import trackingids

    UA_TRACKING_ID = trackingids['webapps-prod'][0]
except:
    print('UA tracking ID not found for Productioon. It should be "webapps-prod" in "trackingids.py"')
    exit(0)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/2.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = os.path.basename(BASE_DIR)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/cspace/' + PROJECT_NAME + '/imagecache',
        'CULL_FREQUENCY': 100000,
        'OPTIONS': {
            'MAX_ENTRIES': 1000000
        }
    }
}
