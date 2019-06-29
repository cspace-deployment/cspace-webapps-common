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
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PARENT_DIR = os.path.dirname(BASE_DIR)
PROJECT_NAME = os.path.basename(BASE_PARENT_DIR)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/home/app_webapps/cache/' + PROJECT_NAME + '/images',
        'CULL_FREQUENCY': 100000,
       'OPTIONS': {
           'MAX_ENTRIES': 1000000
       }
   }
}
