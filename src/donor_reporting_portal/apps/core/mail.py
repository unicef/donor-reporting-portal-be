from anymail.backends import mailjet
from djcelery_email.backends import CeleryEmailBackend
from unicef_notification.backends import EmailBackend as NotificationEmailBackend


class DRPEmailBackend(mailjet.EmailBackend, NotificationEmailBackend):
    pass


class DRPCeleryEmailBackend(mailjet.EmailBackend, CeleryEmailBackend):
    pass
