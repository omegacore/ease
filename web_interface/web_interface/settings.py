"""
Django settings for web_interface project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys
from datetime import datetime

# https://stackoverflow.com/questions/4664724/distributing-django-projects-with-unique-secret-keys/16630719#16630719
# Import/regenerate secret key upon downloading source. Live key should never go to repo
try:
    from .secret_key import SECRET_KEY
except ImportError:
    print("secret_key.py not found! Generating new secret key.")
    settings_dir = os.path.abspath(os.path.dirname(__file__))
    secret_key_filename = os.path.join( settings_dir, 'secret_key.py')
    from django.utils.crypto import get_random_string
    all_chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    with open(secret_key_filename,'w') as sk_file:
        sk_file.write("SECRET_KEY = '"+
            get_random_string(50, all_chars)+
            "'"
        )
    #get_random_string(50, all_chars)
    # import sys
    # sys.exit()
    
    '''
    # wait for file to be created - sometimes there's a delay
    import time
    while not os.path.isfile(secret_key_filename):
        time.sleep(.1)
    from .secret_key import SECRET_KEY
    '''
    sys.exit(0)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = ')9yv30i%h9+3hq3f#1-3t+y*!#jz9l5w%)$d2#&8)w27ibeyz0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

time_stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
top_logs_folder = os.path.join(BASE_DIR, 'session_logs')
if not os.path.exists(top_logs_folder):
    os.mkdir(top_logs_folder)

logs_folder_base = os.path.join(top_logs_folder, 'session_' + time_stamp)
logs_folder = logs_folder_base
idx = 0

while os.path.exists(logs_folder):
    logs_folder = logs_folder_base + "_" + str(idx)
    idx += 1

os.mkdir(logs_folder)

logfile_name = os.path.join(logs_folder, str(os.getpid())+'.log')

if DEBUG:
    handler = 'console'
    django_level = 'INFO'
    app_level = 'DEBUG'
    formatter = 'neat'

else:
    handler = 'file'
    django_level = 'INFO'
    app_level = 'WARNING'
    formatter = 'verbose'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'neat': {
            'format':'[%(asctime)s] %(message)s',
            #srftime format
            'datefmt':'%a %b/%d/%y %I:%M:%S %p',
        },
        'verbose':{
            'format':'[%(asctime)s][%(levelname)s][%(name)s] %(message)s'
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': formatter,
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': logfile_name,
            'when': 'midnight',
            #'interval': 24,
            'backupCount':500,
            'formatter': formatter,
        },
    },
    
    'loggers': {
        'django': {
            'handlers': [handler],
            'level': django_level,
        },
        'alert_config_app': {
            'handlers': [handler],
            'level': app_level,
        },
        'account_mgr_app': {
            'handlers': [handler],
            'level': app_level,
        },
    },
}

ALLOWED_HOSTS = [
    "134.79.165.105",
    "pswww-dev.slac.stanford.edu",
    "198.129.113.193",
    "127.0.0.1"
]
if DEBUG:
    ALLOWED_HOSTS.append("127.0.0.1")
    ALLOWED_HOSTS.append("192.168.225.3")
    ALLOWED_HOSTS.append("192.168.56.101")

if not DEBUG:
    FORCE_SCRIPT_NAME = '/ease'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'alert_config_app',
    'account_mgr_app'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
if not DEBUG:
    MIDDLEWARE.append(
        'whitenoise.middleware.WhiteNoiseMiddleware'
    )


#WHITENOISE_STATIC_PREFIX = FORCE_SCRIPT_NAME
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

if not DEBUG:
    WHITENOISE_STATIC_PREFIX = '/static/'

ROOT_URLCONF = 'web_interface.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['./templates/bases','./templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# set generic lookup location for the fixtures
# Fixtures prepare the django test database with entires for tests
FIXTURE_DIRS = [
    './fixtures',
]

WSGI_APPLICATION = 'web_interface.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

if not DEBUG:
    STATIC_URL = FORCE_SCRIPT_NAME + '/static/'
else:
    STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR,'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR,'staticfiles')

if not DEBUG:
    EMAIL_HOST = 'psmail'
    EMAIL_PORT = 25
    EMAIL_HOST_USER = 'EASE'
    DEFAULT_FROM_EMAIL = 'EASE'
else:
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 2500
    EMAIL_HOST_USER = 'EASE'
    DEFAULT_FROM_EMAIL = 'EASE'


if not DEBUG:
    LOGIN_REDIRECT_URL = FORCE_SCRIPT_NAME + '/alert/title'
    LOGIN_URL = FORCE_SCRIPT_NAME + '/accounts/login'
else:
    LOGIN_REDIRECT_URL = '/alert/title'
    LOGIN_URL = '/accounts/login'

ACCOUNT_ACTIVATION_DAYS = 7
