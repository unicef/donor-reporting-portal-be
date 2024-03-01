from django.contrib.auth.models import AbstractUser

from unicef_security.models import SecurityMixin


class User(AbstractUser, SecurityMixin):
    pass
