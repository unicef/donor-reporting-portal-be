from django.contrib import admin

from unicef_security.admin import UserAdminPlus

from donor_reporting_portal.apps.core.models import User


@admin.register(User)
class UserAdminPlus(UserAdminPlus):
    pass
