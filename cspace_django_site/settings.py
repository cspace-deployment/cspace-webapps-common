"""
Django settings for cspace_django_project project.

"""
import os
import sys
import logging

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = os.path.basename(BASE_DIR)

try:
    from cspace_django_site.extra_settings import *
except ImportError:
    print('you must configure one of the extra_*.py settings files as extra_settings.py!')
    sys.exit(1)

from cspace_django_site.installed_apps import INSTALLED_APPS
from cspace_django_site.webapps_global_config import *

# generate a secret if there isn't one already
try:
    from cspace_django_site.secret_key import *
except ImportError:
    SETTINGS_DIR = os.path.abspath(os.path.dirname(__file__))
    from cspace_django_site.secret_key_gen import *

    generate_secret_key(os.path.join(SETTINGS_DIR, 'secret_key.py'))
    from cspace_django_site.secret_key import *

# this is set in the various "extra_*.py" files
# ALLOWED_HOSTS = []

# Application definition, set in installed_apps.py on a per museum basis
# INSTALLED_APPS =

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cspace_django_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'cspace_django_site/templates/admin'),
            os.path.join(BASE_DIR, 'cspace_django_site/templates/registration'),
            os.path.join(BASE_DIR, 'cspace_django_site/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cspace_django_site.context_processors.ua_tracking_id',
            ],
        },
    },
]

# WSGI_APPLICATION = 'cspace_django_site.wsgi.application'
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'common/templates')]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

# URL prefix for static files.
# Example: "http://intakes.com/static/", "http://static.intakes.com/"
STATIC_URL = '/' + PROJECT_NAME + '_static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, 'client_modules/static_assets/'),
    os.path.join(BASE_DIR, 'webpack_dist'),
)

#
# If the application's WSGI setup script added an environment variable to tell us
# the WSGI mount point path then we should use it; otherwise, we'll assume that
# the application was mounted at the root of the current server
#
WSGI_BASE = os.environ.get(__package__ + ".WSGI_BASE")
if WSGI_BASE is not None:
    pass
    # logging.debug('WSGI_BASE was found in environment variable: ' + __package__ + ".WSGI_BASE")
else:
    # logging.debug('WSGI_BASE was not set.')
    WSGI_BASE = ''

# logging.debug('WSGI_BASE =' + WSGI_BASE)
LOGIN_URL = f'/{PROJECT_NAME}/accounts/login'
LOGIN_REDIRECT_URL = f'/{PROJECT_NAME}/landing'

# we use our special tmp dir for BMU file uploads
# set by importing webapps_global_config above
# FILE_UPLOAD_TEMP_DIR

# LOGGING is set up in the extra_*.py modules

SITE_ID = 2

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

#
# AuthN backends
#
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'authn.authn.CSpaceAuthN',
)

# new django 4 thing, it seems
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# we need this to ensure that forms with lots of fields in them work.
DATA_UPLOAD_MAX_NUMBER_FIELDS = 200000

# we need this to ensure that our webapp proxying works.
# set by importing webapps_global_config above
#CSRF_COOKIE_DOMAIN
