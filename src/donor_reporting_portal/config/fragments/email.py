from ..settings import env

DEFAULT_FROM_EMAIL = "donor_reporting_portal@mail.unicef.org"
EMAIL_BACKEND = "unicef_notification.backends.EmailBackend"
# EMAIL_BACKEND = "donor_reporting_portal.apps.core.backends.EmailBackend"

EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_PORT = env("EMAIL_PORT", default=25)
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env("EMAIL_USE_SSL", default=False)

ANYMAIL = {
    "MAILJET_API_KEY": env("MAILJET_API_KEY", default=""),
    "MAILJET_SECRET_KEY": env("MAILJET_SECRET_KEY", default=""),
}

POST_OFFICE = {
    "DEFAULT_PRIORITY": "now",
    "BACKENDS": {"default": "djcelery_email.backends.CeleryEmailBackend"},
}
