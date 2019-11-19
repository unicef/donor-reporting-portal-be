import datetime
import os
from pathlib import Path

import environ
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

SETTINGS_DIR = Path(__file__).parent
PACKAGE_DIR = SETTINGS_DIR.parent
DEVELOPMENT_DIR = PACKAGE_DIR.parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env()

DEBUG = env.bool('DEBUG')

DATABASES = {'default': env.db()}

INSTALLED_APPS = (
    'donor_reporting_portal.apps.core',
    'donor_reporting_portal.apps.init',
    'donor_reporting_portal.apps.report_metadata',
    'donor_reporting_portal.apps.roles',
    'donor_reporting_portal.apps.sharepoint',
    'donor_reporting_portal.web',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django_extensions',
    'storages',
    'unicef_security',
    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',
    'django_celery_beat',
    'django_celery_results',
    'djcelery_email',
    'corsheaders',
    'social_django',
    'admin_extra_urls',
    'rest_framework_social_oauth2',
    'unicef_vision.vision',
    'post_office',
    'unicef_notification',
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'donor_reporting_portal.apps.core.backends.UnicefAzureADBBCOAuth2',
    'django.contrib.auth.backends.ModelBackend',
    'donor_reporting_portal.apps.core.backends.DonorRoleBackend',
)


# path

MEDIA_ROOT = env('MEDIA_ROOT', default='/tmp/etools/media/')
STATIC_ROOT = env('STATIC_ROOT', default='/tmp/etools/static/')
MEDIA_URL = '/dm-media/'
STATIC_URL = env('STATIC_URL', default='/static/')
STATICFILES_DIRS = []
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = (
    env('ALLOWED_HOST', default='localhost'),
    '0.0.0.0',
)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'


# TIME_ZONE = env('TIME_ZONE')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
ugettext = lambda s: s  # noqa
LANGUAGES = (
    ('es', ugettext('Spanish')),
    ('fr', ugettext('French')),
    ('en', ugettext('English')),
    ('ar', ugettext('Arabic')),
)

SITE_ID = 1
INTERNAL_IPS = ['127.0.0.1', 'localhost']

USE_I18N = True
USE_L10N = True
USE_TZ = True


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

ROOT_URLCONF = 'donor_reporting_portal.config.urls'
WSGI_APPLICATION = 'donor_reporting_portal.config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(PACKAGE_DIR / 'templates')],
        'APP_DIRS': False,
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.app_directories.Loader',
                'unicef_notification.loaders.EmailTemplateLoader',
            ],
            'context_processors': [
                'constance.context_processors.config',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
            'libraries': {
                'staticfiles': 'django.templatetags.static',
                'i18n': 'django.templatetags.i18n',
            },
        },
    },
]


# EMAIL_BACKEND = 'post_office.EmailBackend'
# EMAIL_POST_OFFICE_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST_USER = env('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
# EMAIL_HOST = env('EMAIL_HOST')
# EMAIL_PORT = env.int('EMAIL_PORT')
# EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
# EMAIL_SUBJECT_PREFIX = "[ETOOLS-DRP]"
# POST_OFFICE = {
#     'DEFAULT_PRIORITY': 'now',
#     'BACKENDS': {
#         'default': 'djcelery_email.backends.CeleryEmailBackend'
#     }
# }
# celery-mail
# CELERY_EMAIL_CHUNK_SIZE = 10

# django-secure
# CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_FRAME_DENY = True
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_SECONDS = 1
# SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SESSION_COOKIE_HTTPONLY = env.bool('SESSION_COOKIE_HTTPONLY', default=True)
# SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True)
# X_FRAME_OPTIONS = env('X_FRAME_OPTIONS')
# USE_X_FORWARDED_HOST = env('USE_X_FORWARDED_HOST')
# SESSION_SAVE_EVERY_REQUEST = True

AUTH_USER_MODEL = 'unicef_security.User'

HOST = env('HOST', default='http://localhost:8000')

CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'application/text']
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_BROKER_VISIBILITY_VAR = env('CELERY_VISIBILITY_TIMEOUT', default=1800)  # in seconds
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': int(CELERY_BROKER_VISIBILITY_VAR)}
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
# Sensible settings for celery
CELERY_TASK_ALWAYS_EAGER = env('CELERY_TASK_ALWAYS_EAGER', default=False)
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_PUBLISH_RETRY = True
CELERY_WORKER_DISABLE_RATE_LIMITS = False
CELERY_TASK_IGNORE_RESULT = True
CELERY_SEND_TASK_ERROR_EMAILS = False
CELERY_RESULT_EXPIRES = 600
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

REST_FRAMEWORK = {
    # 'DEFAULT_RENDERER_CLASSES': (
    #     'rest_framework.renderers.JSONRenderer',
    #     'rest_framework.renderers.BrowsableAPIRenderer',
    # ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    # 'PAGE_SIZE': 100,
    # 'DEFAULT_PAGINATION_CLASS': 'unicef_rest_framework.pagination.APIPagination',
    # 'DEFAULT_VERSIONING_CLASS': 'unicef_rest_framework.versioning.URFVersioning',
    # 'SEARCH_PARAM': 'search',
    # 'ORDERING_PARAM': 'ordering',
}

# django-cors-headers: https://github.com/ottoyiu/django-cors-headers
CORS_ORIGIN_ALLOW_ALL = env('CORS_ORIGIN_ALLOW_ALL', default=False)


JWT_AUTH = {
    'JWT_VERIFY': False,  # this requires private key
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 60,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=30000),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,
    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_DECODE_HANDLER': 'rest_framework_jwt.utils.jwt_decode_handler',

    # Keys will be set in core.apps.Config.ready()
    'JWT_PUBLIC_KEY': '?',
    # 'JWT_PRIVATE_KEY': wallet.get_private(),
    # 'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'RS256',

}
SENTRY_DSN = env('SENTRY_DSN', default=None)  # noqa: F405

if SENTRY_DSN:  # pragma: no cover
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # by default this is False, must be set to True so the library attaches the request data to the event
        send_default_pii=True,
        integrations=[DjangoIntegration(), CeleryIntegration()],
    )

if DEBUG:  # pragma: no cover

    INSTALLED_APPS += (  # noqa
        'debug_toolbar',
    )
    MIDDLEWARE += (  # noqa
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TEMPLATE_CONTEXT': True,
    }


VISION_URL = env.str('VISION_URL', 'http://invalid_vision_url')
VISION_USER = env.str('VISION_USER', 'invalid_vision_user')
VISION_PASSWORD = env.str('VISION_PASSWORD', 'invalid_vision_password')
VISION_LOGGER_MODEL = 'vision.VisionLog'

INSIGHT_SUB_KEY = env.str('INSIGHT_SUB_KEY', 'invalid_vision_password')

BUSINESSAREA_MODEL = 'unicef_security.BusinessArea'


SHAREPOINT_TENANT = {
    'url': 'https://asantiagounicef.sharepoint.caaaaaom/',
    'user_credentials': {
        'username': env.str('SHAREPOINT_USERNAME', 'invalid_username'),
        'password': env.str('SHAREPOINT_PASSWORD', 'invalid_password'),
    },
}

SHELL_PLUS_PRE_IMPORTS = (
    ('donor_reporting_portal.config', 'celery'),
)

POST_OFFICE = {
    'DEFAULT_PRIORITY': 'now',
    'BACKENDS': {
        'default': 'djcelery_email.backends.CeleryEmailBackend'
    }
}

DEFAULT_FROM_EMAIL = 'donor_reporting_portal@unicef.org'

# AZURE GRAPH API
# AZURE_TOKEN_URL = 'https://login.microsoftonline.com/unicef.org/oauth2/token'
# AZURE_GRAPH_API_BASE_URL = 'https://graph.microsoft.com'
# AZURE_GRAPH_API_VERSION = 'beta'
# AZURE_GRAPH_API_PAGE_SIZE = 250


KEY = os.getenv('AZURE_B2C_CLIENT_ID', None)
SECRET = os.getenv('AZURE_B2C_CLIENT_SECRET', None)
TENANT_ID = os.getenv('AZURE_B2C_TENANT', 'unicefpartners.onmicrosoft.com')

SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_SANITIZE_REDIRECTS = False
SOCIAL_AUTH_POSTGRES_JSONFIELD = True
POLICY = os.getenv('AZURE_B2C_POLICY_NAME', "B2C_1_signup_signin")
SOCIAL_AUTH_USER_MODEL = 'unicef_security.User'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'donor_reporting_portal.apps.core.auth.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

USER_FIELDS = ['username', 'email', 'first_name', 'last_name']
