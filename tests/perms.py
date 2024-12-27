import operator
from contextlib import ContextDecorator
from functools import reduce
from random import choice
from typing import Iterable

from django.contrib.auth.models import Group, Permission
from django.db.models import Q

from faker import Faker

from donor_reporting_portal.apps.roles.models import UserRole

from .factories import GroupFactory

whitespace = " \t\n\r\v\f"
lowercase = "abcdefghijklmnopqrstuvwxyz"
uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
letters = lowercase + uppercase
ascii_lowercase = lowercase
ascii_uppercase = uppercase
ascii_letters = ascii_lowercase + ascii_uppercase

faker = Faker()


def text(length, choices=ascii_letters):
    """Return a random (fixed length) string.

    :param length: string length
    :param choices: string containing all the chars can be used to build the string

    .. seealso::
       :py:func:`rtext`
    """
    return "".join(choice(choices) for x in range(length))


def get_group(name=None, permissions=None):
    group = GroupFactory(name=(name or text(5)))
    permission_names = permissions or []
    for permission_name in permission_names:
        try:
            app_label, codename = permission_name.split(".")
        except ValueError:
            raise ValueError(f"Invalid permission name `{permission_name}`")
        try:
            permission = Permission.objects.get(content_type__app_label=app_label, codename=codename)
        except Permission.DoesNotExist:
            raise Permission.DoesNotExist("Permission `{0}` does not exists", permission_name)

        group.permissions.add(permission)
    return group


class user_grant_permissions(ContextDecorator):  # noqa
    caches = [
        "_group_perm_cache",
        "_user_perm_cache",
        "_dsspermissionchecker",
        "_officepermissionchecker",
        "_perm_cache",
        "_dss_acl_cache",
    ]

    def __init__(self, user, permissions=None):
        self.user = user
        if not isinstance(permissions, Iterable):
            permissions = [permissions]
        self.permissions = permissions
        self.group = None

    def __enter__(self):
        for cache in self.caches:
            if hasattr(self.user, cache):
                delattr(self.user, cache)
        self.group = get_group(permissions=self.permissions or [])
        self.user.groups.add(self.group)

    def __exit__(self, e_typ, e_val, trcbak):
        if self.group:
            self.user.groups.remove(self.group)
            self.group.delete()

        if e_typ:
            raise e_typ(e_val).with_traceback(trcbak)

    def start(self):
        """Activate a patch, returning any created mock."""
        return self.__enter__()

    def stop(self):
        """Stop an active patch."""
        return self.__exit__(None, None, None)


class user_grant_role_permission:  # noqa
    def __init__(self, user, donor, permissions):
        self.user = user
        self.donor = donor
        self.permissions = permissions

    def __enter__(self):
        if hasattr(self.user, "_group_perm_cache"):
            del self.user._group_perm_cache
        if hasattr(self.user, "_perm_cache"):
            del self.user._perm_cache
        or_queries = []
        if self.permissions:
            self.group, _ = Group.objects.get_or_create(name="context_group")

            for permission in self.permissions:
                app, perm = permission.split(".")
                or_queries.append(Q(codename=perm, content_type__app_label=app))
            self.group.permissions.set(Permission.objects.filter(reduce(operator.or_, or_queries)))
            self.group.save()
            self.user_role, _ = UserRole.objects.get_or_create(user=self.user, group=self.group, donor=self.donor)

    def __exit__(self, e_typ, e_val, trcbak):
        if self.group:
            self.user_role.delete()
            self.group.delete()

    def start(self):
        """Activate a patch, returning any created mock."""
        return self.__enter__()

    def stop(self):
        """Stop an active patch."""
        return self.__exit__()
