from django.contrib.auth.models import AbstractUser

from unicef_security.models import SecurityMixin, TimeStampedModel


class User(AbstractUser, SecurityMixin, TimeStampedModel):
    pass
