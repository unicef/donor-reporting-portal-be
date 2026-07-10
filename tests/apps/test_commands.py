import os
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import OperationalError

import pytest

pytestmark = pytest.mark.slow


@pytest.fixture
def autocreate_users():
    os.environ["AUTOCREATE_USERS"] = "user1,pwd|user2,pwd"
    yield
    del os.environ["AUTOCREATE_USERS"]


@pytest.fixture
def invalidate_cache():
    os.environ["INVALIDATE_CACHE"] = "1"
    yield
    del os.environ["INVALIDATE_CACHE"]


@pytest.mark.django_db
def test_db_is_ready(db, monkeypatch):
    monkeypatch.setattr("sys.exit", lambda v: v)
    call_command("db_isready", stdout=StringIO(), stderr=StringIO())


@pytest.mark.django_db
def test_db_is_ready_error(db, monkeypatch):
    monkeypatch.setattr("sys.exit", lambda v: v)
    with mock.patch(
        "donor_reporting_portal.apps.core.management.commands.db_isready.Command._get_cursor",
        side_effect=OperationalError(),
    ):
        call_command("db_isready", wait=True, timeout=1, stdout=StringIO(), stderr=StringIO())


@pytest.mark.django_db
def test_db_is_ready_debug(db, monkeypatch):
    monkeypatch.setattr("sys.exit", lambda v: v)
    with mock.patch(
        "donor_reporting_portal.apps.core.management.commands.db_isready.Command._get_cursor",
        side_effect=OperationalError(),
    ):
        call_command(
            "db_isready",
            wait=True,
            timeout=1,
            debug=True,
            stdout=StringIO(),
            stderr=StringIO(),
        )


@pytest.mark.django_db
def test_upgrade_collectstatic(db):
    out = StringIO()
    with mock.patch("donor_reporting_portal.apps.core.management.commands.upgrade.call_command") as mock_call:
        call_command("upgrade", collectstatic=True, stdout=out, stderr=StringIO())
    mock_call.assert_called_once_with("collectstatic", verbosity=0, interactive=False)


@pytest.mark.django_db
def test_upgrade_migrate(db):
    out = StringIO()
    with mock.patch("donor_reporting_portal.apps.core.management.commands.upgrade.call_command") as mock_call:
        call_command("upgrade", migrate=True, stdout=out, stderr=StringIO())
    mock_call.assert_called_once_with("migrate", verbosity=0)


@pytest.mark.django_db
def test_upgrade_users_no_password(db):
    out = StringIO()
    with mock.patch("donor_reporting_portal.apps.core.management.commands.upgrade.call_command") as mock_call:
        call_command("upgrade", users=True, stdout=out, stderr=StringIO())
    mock_call.assert_called_once_with("update_notifications", verbosity=0)


@pytest.mark.django_db
def test_upgrade_users_with_password(db, monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", "testpass123")
    out = StringIO()
    with mock.patch("donor_reporting_portal.apps.core.management.commands.upgrade.call_command") as mock_call:
        call_command("upgrade", users=True, stdout=out, stderr=StringIO())
    mock_call.assert_called_once_with("update_notifications", verbosity=0)
    get_user_model().objects.get(username="admin")


@pytest.mark.django_db
def test_upgrade_stale_ct(db):
    out = StringIO()
    with mock.patch("donor_reporting_portal.apps.core.management.commands.upgrade.call_command") as mock_call:
        call_command("upgrade", stale_ct=True, stdout=out, stderr=StringIO())
    mock_call.assert_called_once_with("remove_stale_contenttypes", verbosity=0, interactive=False)


@pytest.mark.django_db
def test_upgrade_permissions(db):
    out = StringIO()
    with mock.patch("donor_reporting_portal.apps.core.management.commands.upgrade.call_command") as mock_call:
        call_command("upgrade", permissions=True, stdout=out, stderr=StringIO())
    mock_call.assert_called_once_with("update_permissions", verbosity=0)


@pytest.mark.django_db
def test_upgrade_metadata(db):
    out = StringIO()
    with mock.patch("donor_reporting_portal.apps.core.management.commands.upgrade.call_command") as mock_call:
        call_command("upgrade", metadata=True, stdout=out, stderr=StringIO())
    assert mock_call.call_count == 3
    mock_call.assert_has_calls(
        [
            mock.call("loaddata", "groups.json"),
            mock.call("loaddata", "libraries.json"),
            mock.call("loaddata", "metadata.json"),
        ]
    )


@pytest.mark.django_db
def test_upgrade_all(db, monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", "testpass123")
    out = StringIO()
    with mock.patch("donor_reporting_portal.apps.core.management.commands.upgrade.call_command") as mock_call:
        call_command("upgrade", all=True, stdout=out, stderr=StringIO())
    assert mock_call.call_count == 8
    mock_call.assert_has_calls(
        [
            mock.call("collectstatic", verbosity=0, interactive=False),
            mock.call("migrate", verbosity=0),
            mock.call("update_notifications", verbosity=0),
            mock.call("remove_stale_contenttypes", verbosity=0, interactive=False),
            mock.call("update_permissions", verbosity=0),
            mock.call("loaddata", "groups.json"),
            mock.call("loaddata", "libraries.json"),
            mock.call("loaddata", "metadata.json"),
        ],
        any_order=True,
    )
