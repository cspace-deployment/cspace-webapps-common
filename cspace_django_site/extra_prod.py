# settings needed for Production
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = os.path.basename(BASE_DIR)

from cspace_django_site.webapps_global_config import *

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

# 8 rotating logs, 32MB each, named '<museum>.webapps.log.txt', only INFO or higher
# emailing of ERROR level messages deferred for now: we'd need to configure all that
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'timestamp': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        # 'mail_admins': {
        #     'level': 'ERROR',
        #     'class': 'django.utils.log.AdminEmailHandler',
        #     'filters': ['require_debug_false']
        # },
        'logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'timestamp',
            'filename': os.path.join(WEBAPPS_LOGS_DIR, f'{PROJECT_NAME}.webapps.log'),
            'maxBytes': 32 * 1024 * 1024,
            'backupCount': 8,
            'encoding': 'utf8',
        },
    },
    'loggers': {
        # 'django.request': {
        #     'handlers': ['mail_admins'],
        #     'level': 'ERROR',
        #     'propagate': False,
        # },
        # TODO: why does this work, even required: '' as logger
        '': {
            'handlers': ['logfile'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}