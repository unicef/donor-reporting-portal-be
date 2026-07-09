import pytest


def test_notify_donor_template():
    from donor_reporting_portal.apps.report_metadata.notifications.notify_donor import (
        defaults,
        name,
    )

    assert name == "notify_donor"
    assert "subject" in defaults


def test_notify_gavi_template():
    from donor_reporting_portal.apps.report_metadata.notifications.notify_gavi import (
        defaults,
        name,
    )

    assert name == "notify_gavi"
    assert "subject" in defaults


def test_notify_urgent_gavi_template():
    from donor_reporting_portal.apps.report_metadata.notifications.notify_urgent_gavi import (
        defaults,
        name,
    )

    assert name == "notify_urgent_gavi"
    assert "subject" in defaults


@pytest.mark.django_db
def test_access_grant_email_template():
    from donor_reporting_portal.apps.roles.notifications.access_grant_email import (
        defaults,
        name,
    )

    assert name == "access_grant_email"
    assert "subject" in defaults
