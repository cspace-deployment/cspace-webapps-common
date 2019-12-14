import os

# settings needed for Production

try:
    # get the tracking id for Prod
    from cspace_django_site.trackingids import trackingids

    UA_TRACKING_ID = trackingids['webapps-prod'][0]
except:
    print('UA tracking ID not found for Production. It should be "webapps-prod" in "trackingids.py"')
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

# 8 rotating logs, 16MB each, named '<museum>.webapps.log.txt', only INFO or higher
# emailing of ERROR level messages deferred for now: we'd need to configure all that
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # 'formatters': {
    # },
    # 'filters': {
    #     'require_debug_false': {
    #         '()': 'django.utils.log.RequireDebugFalse'
    #     }
    # },
    'handlers': {
        # 'mail_admins': {
        #     'level': 'ERROR',
        #     'class': 'django.utils.log.AdminEmailHandler',
        #     'filters': ['require_debug_false']
        # },
        'logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('/', 'var', 'log', 'django', PROJECT_NAME, f'{PROJECT_NAME}.webapps.log'),
            'maxBytes': 16 * 1024 * 1024,
            'backupCount': 8,
            # 'formatter': 'standard',
        },
    },
    'loggers': {
        # 'django.request': {
        #     'handlers': ['mail_admins'],
        #     'level': 'ERROR',
        #     'propagate': False,
        # },
        '': {
            'handlers': ['logfile'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}