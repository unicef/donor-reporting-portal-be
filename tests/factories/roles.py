from django.contrib.auth.models import Group

import factory
import unicef_security
from factory import SubFactory
from tests.factories import DonorFactory
from unicef_security.models import BusinessArea, Region

from donor_reporting_portal.apps.roles.models import UserRole


class GroupFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: "name%03d" % n)

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if not create:
            return  # Simple build, do nothing.

        if extracted:
            for permission in extracted:  # A list of groups were passed in, use them
                self.permissions.add(permission)

    class Meta:
        model = Group
        django_get_or_create = ('name',)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = unicef_security.models.User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: "user%03d" % n)

    last_name = factory.Faker('last_name')
    first_name = factory.Faker('first_name')

    email = factory.Sequence(lambda n: "m%03d@mailinator.com" % n)
    password = 'password'
    is_superuser = False
    is_active = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        from ..perms import user_grant_permissions

        permissions = kwargs.pop('permissions', [])

        password = kwargs.pop('password')
        user = super()._prepare(cls, create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        user_grant_permissions(user, permissions).start()
        return user


class AdminFactory(UserFactory):
    is_superuser = True


class AnonUserFactory(UserFactory):
    username = 'anonymous'


class RegionFactory(factory.DjangoModelFactory):
    code = factory.Sequence(lambda n: "code%03d" % n)
    name = factory.Sequence(lambda n: "name%03d" % n)

    class Meta:
        model = Region
        django_get_or_create = ('name',)


class BusinessAreaFactory(factory.DjangoModelFactory):
    code = factory.Sequence(lambda n: "code%03d" % n)
    region = SubFactory(RegionFactory)

    class Meta:
        model = BusinessArea
        django_get_or_create = ('code',)


class UserRoleFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
    donor = factory.SubFactory(DonorFactory)

    class Meta:
        model = UserRole
