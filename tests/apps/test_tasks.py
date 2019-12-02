from unittest import mock

from donor_reporting_portal.apps.report_metadata.tasks import grant_sync


def test_grant_sync_url(django_app, admin_user):
    with mock.patch('donor_reporting_portal.apps.report_metadata.tasks.GrantSynchronizer'):
        grant_sync()
