import os
from pathlib import Path

import environ

SETTINGS_DIR = Path(__file__).parent
PACKAGE_DIR = SETTINGS_DIR.parent
DEVELOPMENT_DIR = PACKAGE_DIR.parent.parent

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env()

DEBUG = env.bool("DEBUG")

DATABASES = {"default": env.db(default="psql://postgres:pass@db:5432/postgres")}

INSTALLED_APPS = (
    "donor_reporting_portal.apps.core",
    "donor_reporting_portal.apps.report_metadata",
    "donor_reporting_portal.apps.roles",
    "donor_reporting_portal.apps.sharepoint",
    "donor_reporting_portal.web",
    "sharepoint_rest_api",
    "unicef_security",
    "unicef_realm",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django.contrib.admin",
    "django.contrib.humanize",
    "django_extensions",
    "django_filters",
    "rest_framework",
    "rest_framework.authtoken",
    "django_celery_beat",
    "django_celery_results",
    "djcelery_email",
    "corsheaders",
    "social_django",
    "admin_extra_buttons",
    "adminactions",
    "rest_framework_social_oauth2",
    "unicef_vision.vision",
    "post_office",
    "unicef_notification",
    "impersonate",
)

MIDDLEWARE = (
    "unicef_djangolib.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "impersonate.middleware.ImpersonateMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "unicef_security.middleware.UNICEFSocialAuthExceptionMiddleware",
)

AUTHENTICATION_BACKENDS = (
    "donor_reporting_portal.apps.core.backends.UNICEFAzureADB2COAuth2",
    "django.contrib.auth.backends.ModelBackend",
    "donor_reporting_portal.apps.core.backends.DonorRoleBackend",
)

SOCIAL_AUTH_BACKEND_NAME = "unicef-azuread-b2c-oauth2"


# path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
MEDIA_ROOT = env("MEDIA_ROOT", default="/tmp/etools/media/")  # noqa
STATIC_ROOT = env("STATIC_ROOT", default=os.path.join(BASE_DIR, "static"))
MEDIA_URL = "/dm-media/"
STATIC_URL = env("STATIC_URL", default="/static/")
STATICFILES_DIRS = []
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

SECRET_KEY = env("SECRET_KEY")
HOST = env("HOST", default="http://localhost:8000")
ALLOWED_HOSTS = (env("ALLOWED_HOST", default="localhost"),)

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_URL = "/accounts/logout"
LOGOUT_REDIRECT_URL = "/landing/"

LANGUAGE_CODE = "en-us"
ugettext = lambda s: s  # noqa
LANGUAGES = (
    ("es", ugettext("Spanish")),
    ("fr", ugettext("French")),
    ("en", ugettext("English")),
    ("ar", ugettext("Arabic")),
)

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
SITE_ID = 1
INTERNAL_IPS = ["127.0.0.1", "localhost"]

USE_I18N = True
USE_TZ = True

ROOT_URLCONF = "donor_reporting_portal.config.urls"
WSGI_APPLICATION = "donor_reporting_portal.config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(PACKAGE_DIR / "templates")],
        "APP_DIRS": False,
        "OPTIONS": {
            "loaders": [
                "django.template.loaders.app_directories.Loader",
                "unicef_notification.loaders.EmailTemplateLoader",
            ],
            "context_processors": [
                "constance.context_processors.config",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
            "libraries": {
                "staticfiles": "django.templatetags.static",
                "i18n": "django.templatetags.i18n",
            },
        },
    },
]

AUTH_USER_MODEL = "core.User"
BUSINESSAREA_MODEL = "unicef_security.BusinessArea"
REALM_TARGET_MODEL = "unicef_realm.BusinessArea"

if DEBUG:  # pragma: no cover
    INSTALLED_APPS += ("debug_toolbar",)  # noqa
    MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)  # noqa
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TEMPLATE_CONTEXT": True,
    }

SHELL_PLUS_PRE_IMPORTS = (("donor_reporting_portal.config", "celery"),)

from .fragments import *  # noqa
