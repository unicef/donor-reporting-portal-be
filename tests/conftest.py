import os
import tempfile

from django.core.management import call_command

import pytest
from rest_framework.test import APIClient


def pytest_configure(config):
    # enable this to remove deprecations
    os.environ['CELERY_TASK_ALWAYS_EAGER'] = "1"
    os.environ['STATIC_ROOT'] = tempfile.gettempdir()



@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'notifications.json')


@pytest.fixture()
def client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture()
def user(request, db):
    from tests.factories import UserFactory
    return UserFactory()


@pytest.fixture()
def logged_user(client, user):
    client.force_authenticate(user)
    return user


@pytest.fixture()
def business_area():
    from .factories import BusinessAreaFactory
    return BusinessAreaFactory()


@pytest.fixture()
def userrole():
    from .factories import UserRoleFactory
    return UserRoleFactory()


@pytest.fixture()
def theme():
    from .factories import ThemeFactory
    return ThemeFactory()


@pytest.fixture()
def donor():
    from .factories import DonorFactory
    return DonorFactory()


@pytest.fixture()
def external_grant():
    from .factories import ExternalGrantFactory
    return ExternalGrantFactory()


@pytest.fixture()
def grant():
    from .factories import GrantFactory
    return GrantFactory()


@pytest.fixture()
def group():
    from .factories import GroupFactory
    return GroupFactory()
