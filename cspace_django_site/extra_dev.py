# settings needed for Development
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = os.path.basename(BASE_DIR)

try:
    # get the tracking id for Dev
    from cspace_django_site.trackingids import trackingids

    UA_TRACKING_ID = trackingids['webapps-dev'][0]
except:
    print('UA tracking ID not found for Development. It should be "webapps-dev" in "trackingids.py"')
    exit(0)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/2.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# 8 rotating logs, 16MB each, named '<museum>.webapps.log.txt', only INFO or higher
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
        'logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'timestamp',
            'filename': os.path.join('/', 'var', 'log', 'django', PROJECT_NAME, f'{PROJECT_NAME}.webapps.log'),
            'maxBytes': 16 * 1024 * 1024,
            'backupCount': 8,
            'encoding': 'utf8',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['logfile'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
