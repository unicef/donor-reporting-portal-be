import pytest

from donor_reporting_portal.apps.report_metadata.notifications.notify_donor import (
    defaults as donor_defaults,
    name as donor_name,
)
from donor_reporting_portal.apps.report_metadata.notifications.notify_gavi import (
    defaults as gavi_defaults,
    name as gavi_name,
)
from donor_reporting_portal.apps.report_metadata.notifications.notify_urgent_gavi import (
    defaults as urgent_gavi_defaults,
    name as urgent_gavi_name,
)
from donor_reporting_portal.apps.roles.notifications.access_grant_email import (
    defaults as access_grant_defaults,
    name as access_grant_name,
)


def test_notify_donor_template():
    assert donor_name == "notify_donor"
    assert "subject" in donor_defaults


def test_notify_gavi_template():
    assert gavi_name == "notify_gavi"
    assert "subject" in gavi_defaults


def test_notify_urgent_gavi_template():
    assert urgent_gavi_name == "notify_urgent_gavi"
    assert "subject" in urgent_gavi_defaults


@pytest.mark.django_db
def test_access_grant_email_template():
    assert access_grant_name == "access_grant_email"
    assert "subject" in access_grant_defaults
