"""
Django settings for democracylab project.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
#TODO: Call out any missing required environment variables during startup
import os
import ast
import dj_database_url
from datetime import timedelta
from dateutil.parser import parse
from distutils.util import strtobool
from django.core.mail.backends.smtp import EmailBackend

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = strtobool(os.environ.get('DJANGO_DEBUG'))

ALLOWED_HOSTS = ['*']

S3_BUCKET = os.environ.get('S3_BUCKET')

# Application definition

INSTALLED_APPS = [
    'civictechprojects.apps.CivictechprojectsConfig',
    'common.apps.CommonConfig',
    'democracylab.apps.DemocracylabConfig',
    'oauth2.apps.OAuth2Config',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'rest_framework',
    'taggit',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'oauth2.providers.github',
    'oauth2.providers.google',
    'oauth2.providers.linkedin',
    'oauth2.providers.facebook',
    'django_seo_js'
]

SITE_ID = 1

# Customize allauth.socialaccount
SOCIALACCOUNT_ADAPTER = 'oauth2.adapter.SocialAccountAdapter'
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_AUTO_SIGNUP = True  # Bypass the signup form
SOCIALACCOUNT_STORE_TOKENS = False  # Token table has foreign key on SocialApp table, which we're not using
SOCIAL_APPS_environ = os.environ.get('SOCIAL_APPS', None)
if SOCIAL_APPS_environ is not None:
    SOCIAL_APPS = ast.literal_eval(SOCIAL_APPS_environ)
    SOCIAL_APPS_VISIBILITY = {app: SOCIAL_APPS[app]["public"] for app in SOCIAL_APPS.keys()}

SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'SCOPE': ['read:user']
    },
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'}
    },
    'linkedin': {
        'SCOPE': ['r_liteprofile', 'r_emailaddress']
    },
    'facebook': {
        'SCOPE': ['email', 'public_profile'],
         'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
         'METHOD': 'oauth2'  # instead of 'js_sdk'
    },
}

GITHUB_API_TOKEN = os.environ.get('GITHUB_API_TOKEN', None)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# TODO: Use     'django_seo_js.middleware.UserAgentMiddleware',
MIDDLEWARE = [
    'common.helpers.caching.DebugUserAgentMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'democracylab.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_ROOT, 'democracylab/templates'),
            os.path.join(PROJECT_ROOT, 'democracylab/templates/emails'),
            os.path.join(PROJECT_ROOT, 'civictechprojects/templates')
        ],
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

WSGI_APPLICATION = 'democracylab.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DL_DATABASE = os.environ.get('DL_DATABASE', '')
HOSTNAME = os.environ.get('HOSTNAME', '127.0.0.1')

DATABASES = ast.literal_eval(DL_DATABASE) if DL_DATABASE else {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'p0stgres!',
        'HOST': HOSTNAME,
        'PORT': '5432',
    }
}

db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)

LOGIN_REDIRECT_URL = '/'

#Caching number of tag counts only for now - change this if other things are db-cached
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'default_db_cache',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

# Make sure to keep these in sync with the validators in SignUpController.jsx
# TODO: Find a validator for verifying password contains at least 1 number, letter, and non-alphanumeric character
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
    ],
    'PAGE_SIZE': 10
}


def read_connection_config(config):
    return config and {
        'from_name': '{name} <{email_address}>'.format(name=config['display_name'], email_address=config['username']),
        'connection': EmailBackend(
            host=config['host'],
            port=int(config['port']),
            username=config['username'],
            password=config['password'],
            use_tls=strtobool(config['use_tls']),
            fail_silently=False,
            use_ssl=strtobool(config['use_ssl']),
            timeout=None,
            ssl_keyfile=None,
            ssl_certfile=None)
    }

EMAIL_SUPPORT_ACCT = read_connection_config(ast.literal_eval(os.environ.get('EMAIL_SUPPORT_ACCT', 'None')))
EMAIL_VOLUNTEER_ACCT = read_connection_config(ast.literal_eval(os.environ.get('EMAIL_VOLUNTEER_ACCT', 'None')))

# Default log to console in the absence of any account configurations
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

PROTOCOL_DOMAIN = os.environ['PROTOCOL_DOMAIN']
ADMIN_EMAIL = os.environ['ADMIN_EMAIL']
CONTACT_EMAIL = os.environ['CONTACT_EMAIL']
FAKE_EMAILS = not EMAIL_SUPPORT_ACCT or not EMAIL_VOLUNTEER_ACCT or os.environ.get('FAKE_EMAILS', False) == 'True'

MAILCHIMP_API_KEY = os.environ.get('MAILCHIMP_API_KEY', None)
MAILCHIMP_SUBSCRIBE_LIST_ID = os.environ.get('MAILCHIMP_SUBSCRIBE_LIST_ID', None)

APPLICATION_REMINDER_PERIODS = ast.literal_eval(os.environ.get('APPLICATION_REMINDER_PERIODS', 'None'))
VOLUNTEER_RENEW_REMINDER_PERIODS = ast.literal_eval(os.environ.get('VOLUNTEER_RENEW_REMINDER_PERIODS', 'None'))
VOLUNTEER_REMINDER_OVERALL_PERIOD = VOLUNTEER_RENEW_REMINDER_PERIODS and timedelta(sum(VOLUNTEER_RENEW_REMINDER_PERIODS))
VOLUNTEER_CONCLUDE_SURVEY_URL = os.environ.get('VOLUNTEER_CONCLUDE_SURVEY_URL', '')


DLAB_PROJECT_ID = os.environ.get('DLAB_PROJECT_ID', None)

PAYPAL_ENDPOINT = os.environ.get('PAYPAL_ENDPOINT', '')
PAYPAL_PAYEE = os.environ.get('PAYPAL_PAYEE', '')

SPONSORS_METADATA = os.environ.get('SPONSORS_METADATA', '')

HEADER_ALERT = os.environ.get('HEADER_ALERT', '')

PROJECT_DESCRIPTION_EXAMPLE_URL = os.environ.get('PROJECT_DESCRIPTION_EXAMPLE_URL', '')
POSITION_DESCRIPTION_EXAMPLE_URL = os.environ.get('POSITION_DESCRIPTION_EXAMPLE_URL', '')

PRESS_LINKS = os.environ.get('PRESS_LINKS', '')

SECURE_SSL_REDIRECT = os.environ.get('DL_SECURE_SSL_REDIRECT', False) == 'True'

# Note: This environment variable should only be applied in Production
HOTJAR_APPLICATION_ID = os.environ.get('HOTJAR_APPLICATION_ID', '')

GOOGLE_PROPERTY_ID = os.environ.get('GOOGLE_PROPERTY_ID', '')
GOOGLE_ADS_ID = os.environ.get('GOOGLE_ADS_ID', '')
GOOGLE_TAGS_ID = os.environ.get('GOOGLE_TAGS_ID', '')
GOOGLE_CONVERSION_IDS = ast.literal_eval(os.environ.get('GOOGLE_CONVERSION_IDS', 'None'))

#Google ReCaptcha keys - site key is exposed to the front end, secret is not
GR_SITEKEY = os.environ.get('GOOGLE_RECAPTCHA_SITE_KEY', '')
GR_SECRETKEY = os.environ.get('GOOGLE_RECAPTCHA_SECRET_KEY', '')

STATIC_CDN_URL = os.environ.get('STATIC_CDN_URL', '')

ENVIRONMENT_VARIABLE_WARNINGS = {
    'PRESS_LINKS': {
        'error': True,
        'message': 'Press page articles will not be shown.'
    },
    'PROTOCOL_DOMAIN': {
        'error': True,
        'message': 'Backend link generation will not work.'
    },
    'BOARD_OF_DIRECTORS': {
        'error': False,
        'message': 'About Us page will not display correctly.'
    },
    'DLAB_PROJECT_ID': {
        'error': False,
        'message': 'About Us page will not display correctly.'
    },
    'STATIC_CDN_URL': {
        'error': False,
        'message': 'Static images will not be shown.'
    },
    'PROJECT_DESCRIPTION_EXAMPLE_URL': {
        'error': False,
        'message': 'Example url for project description will not be shown.'
    },
    'POSITION_DESCRIPTION_EXAMPLE_URL': {
        'error': False,
        'message': 'Example url for position description will not be shown.'
    },
    'S3_BUCKET': {
        'error': False,
        'message': 'Saving images and files will not work.'
    },
    'PAYPAL_ENDPOINT': {
        'error': False,
        'message': 'Donations will not work.'
    },
    'VOLUNTEER_RENEW_REMINDER_PERIODS': {
        'error': False,
        'message': 'Needed to calculate volunteer renewal periods.'
    },
    'GR_SITEKEY': {
        'error': True,
        'message': 'Contact Us page will not render correctly.'
    },
    'CONTACT_EMAIL': {
        'error': False,
        'message': 'Contact Us form will not send messages.'
    },
    'GITHUB_API_TOKEN': {
        'error': False,
        'message': 'Github API key needed to raise rate limit for ingesting commit data'
    },
    'MAILCHIMP_API_KEY': {
        'error': False,
        'message': 'Mailchimp API key needed to subscribe users to mailing list'
    }
}

# TODO: Set to True in productions
# SESSION_COOKIE_SECURE = True

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

PROJECTS_PER_PAGE = os.environ.get('PROJECTS_PER_PAGE', 20)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'custom_error_handler': {
            'class': 'democracylab.logging.CustomErrorHandler'
        }
    },
    'loggers': {
        # Override global logger
        '': {
            'handlers': ['custom_error_handler'],
            'level': 'ERROR',
            'propagate': True
        },
    },
}

# If you're using prerender.io (the default backend):
SEO_JS_PRERENDER_TOKEN = os.environ.get('SEO_JS_PRERENDER_TOKEN', '')
SEO_JS_BACKEND = "common.helpers.caching.DebugPrerenderIO"
SEO_JS_PRERENDER_URL = os.environ.get('SEO_JS_PRERENDER_URL', 'http://localhost:3000/')  # Note trailing slash.
SEO_JS_PRERENDER_RECACHE_URL = SEO_JS_PRERENDER_URL + "recache"
SEO_JS_ENABLED = os.environ.get('SEO_JS_ENABLED', False) == 'True'

# TODO: Put in environment variable
SEO_JS_USER_AGENTS = (
    # These first three should be disabled, since they support escaped fragments, and
    # and leaving them enabled will penalize a website as "cloaked".
    "Googlebot",
    "Yahoo",
    "bingbot",

    "Ask Jeeves",
    "baiduspider",
    "facebookexternalhit",
    "twitterbot",
    "rogerbot",
    "linkedinbot",
    "embedly",
    "quoralink preview'",
    "showyoubot",
    "outbrain",
    "pinterest",
    "developersgoogle.com/+/web/snippet",
)

DISALLOW_CRAWLING = os.environ.get('DISALLOW_CRAWLING', False) == 'True'

DL_PAGES_LAST_UPDATED_DATE = os.environ.get('DL_PAGES_LAST_UPDATED', '2019-12-05')
SITE_LAST_UPDATED = parse(DL_PAGES_LAST_UPDATED_DATE)

# https://docs.djangoproject.com/en/1.7/ref/settings/#silenced-system-checks
SILENCED_SYSTEM_CHECKS = ["rest_framework.W001"]

# How many of the most recent github commits to store per project.
MAX_COMMITS_PER_PROJECT = int(os.environ.get('MAX_COMMITS_PER_PROJECT', 30))

BOARD_OF_DIRECTORS = os.environ.get('BOARD_OF_DIRECTORS', '')

FAVICON_PATH = os.environ.get('FAVICON_PATH', 'https://d1agxr2dqkgkuy.cloudfront.net/img/favicon.png')