import os
import tempfile

from django.core.management import call_command

import pytest
from rest_framework.test import APIClient

from factories import (
    BusinessAreaFactory,
    DonorFactory,
    ExternalGrantFactory,
    GrantFactory,
    GroupFactory,
    SecondaryDonorFactory,
    SharePointGroupFactory,
    ThemeFactory,
    UserFactory,
    UserRoleFactory,
)


def pytest_configure(config):
    os.environ["STATIC_ROOT"] = tempfile.gettempdir()


@pytest.fixture(autouse=True)
def use_override_settings(settings):
    os.environ["SECRET_KEY"] = "6311bc92d3d1ebf12ae2aa54d8aaeeafa9e8cdb4"
    os.environ["CELERY_TASK_ALWAYS_EAGER"] = "1"
    os.environ["STATIC_ROOT"] = tempfile.gettempdir()


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "notifications.json")


@pytest.fixture
def client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def user(request, db):
    return UserFactory()


@pytest.fixture
def logged_user(client, user):
    client.force_authenticate(user)
    return user


@pytest.fixture
def business_area():
    return BusinessAreaFactory()


@pytest.fixture
def userrole():
    return UserRoleFactory()


@pytest.fixture
def theme():
    return ThemeFactory()


@pytest.fixture
def donor():
    return DonorFactory()


@pytest.fixture
def sharepoint_group():
    return SharePointGroupFactory()


@pytest.fixture
def external_grant():
    return ExternalGrantFactory()


@pytest.fixture
def grant():
    return GrantFactory()


@pytest.fixture
def secondary_donor():
    return SecondaryDonorFactory()


@pytest.fixture
def group():
    return GroupFactory()
