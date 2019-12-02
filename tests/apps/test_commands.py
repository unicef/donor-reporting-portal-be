import os
from io import StringIO
from unittest import mock
from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import OperationalError

import pytest

pytestmark = pytest.mark.slow


@pytest.fixture()
def autocreate_users():
    os.environ['AUTOCREATE_USERS'] = "user1,pwd|user2,pwd"
    yield
    del os.environ['AUTOCREATE_USERS']


@pytest.fixture()
def invalidate_cache():
    os.environ['INVALIDATE_CACHE'] = "1"
    yield
    del os.environ['INVALIDATE_CACHE']


@pytest.mark.django_db
def test_db_is_ready(db, monkeypatch):
    monkeypatch.setattr("sys.exit", lambda v: v)
    call_command("db-isready", stdout=StringIO(), stderr=StringIO())


@pytest.mark.django_db
def test_db_is_ready_error(db, monkeypatch):
    monkeypatch.setattr("sys.exit", lambda v: v)
    with mock.patch('donor_reporting_portal.apps.init.management.commands.db-isready.Command._get_cursor',
                    side_effect=OperationalError()):
        call_command("db-isready", wait=True, timeout=1,
                     stdout=StringIO(), stderr=StringIO())


@pytest.mark.django_db
def test_db_is_ready_debug(db, monkeypatch):
    monkeypatch.setattr("sys.exit", lambda v: v)
    with mock.patch('donor_reporting_portal.apps.init.management.commands.db-isready.Command._get_cursor',
                    side_effect=OperationalError()):
        call_command("db-isready", wait=True, timeout=1, debug=True,
                     stdout=StringIO(), stderr=StringIO())
