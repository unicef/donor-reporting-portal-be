from unittest import mock

import pytest
from django.conf import settings
from django.test import Client


from factories import DonorFactory, UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_user():
    return UserFactory(is_staff=True, is_superuser=True)


@pytest.fixture
def admin_client(admin_user):
    client = Client()
    client.force_login(admin_user)
    return client


class TestDonorAdminNotifyButton:
    def test_regular_donor_dispatches_notify_donor(self, admin_client):
        donor = DonorFactory(name="Test Donor", code="REG01")
        url = f"/admin/report_metadata/donor/{donor.pk}/_send_notifications/"
        with mock.patch("donor_reporting_portal.apps.report_metadata.admin.notify_donor") as mock_notify:
            response = admin_client.post(url)
        assert response.status_code == 302
        mock_notify.delay.assert_called_once_with(donor.code)

    def test_gavi_donor_dispatches_notify_gavi_donor(self, admin_client):
        donor = DonorFactory(name="GAVI", code=settings.GAVI_DONOR_CODE)
        url = f"/admin/report_metadata/donor/{donor.pk}/_send_notifications/"
        with mock.patch("donor_reporting_portal.apps.report_metadata.admin.notify_gavi_donor") as mock_notify:
            response = admin_client.post(url)
        assert response.status_code == 302
        mock_notify.delay.assert_called_once_with(donor.code)

    def test_redirects_back_to_donor_change(self, admin_client):
        donor = DonorFactory(name="Test Donor", code="REG02")
        url = f"/admin/report_metadata/donor/{donor.pk}/_send_notifications/"
        with mock.patch("donor_reporting_portal.apps.report_metadata.admin.notify_donor"):
            response = admin_client.post(url)
        assert response.status_code == 302
        assert f"/admin/report_metadata/donor/{donor.pk}/change/" in response.url
