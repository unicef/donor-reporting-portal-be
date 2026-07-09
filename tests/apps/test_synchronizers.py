from pathlib import Path

from django.test.utils import override_settings

import pytest
from vcrpy import VCR

from donor_reporting_portal.apps.report_metadata.models import Donor, ExternalGrant, Grant, SecondaryDonor
from donor_reporting_portal.apps.report_metadata.synchronizers import GrantSynchronizer


@pytest.mark.django_db
@override_settings(INSIGHT_URL="http://invalid_vision_url")
@VCR.use_cassette(str(Path(__file__).parent / "vcr_cassettes/test_grant_sync.yml"))
def test_grant_sync():
    assert Donor.objects.count() == 0
    assert Grant.objects.count() == 0
    assert ExternalGrant.objects.count() == 0
    GrantSynchronizer().sync()
    assert Donor.objects.count() == 6
    assert Grant.objects.count() == 7
    assert ExternalGrant.objects.count() == 4


@pytest.mark.django_db
def test_item_save_mismatched_secondary_donors():
    record = {
        "DONOR_CODE": "D001",
        "DONOR_NAME": "Donor One",
        "GRANT_REF": "GRANT-001",
        "ISSUE_YEAR": "2024",
        "EXPIRY_DATE": None,
        "FINANCIALLY_CLOSE_DATE": None,
        "DESCRIPTION": "Test grant",
        "USGOV_FLAG": "",
        "THEMATIC": "",
        "EXTERNAL_REF": "",
        "RECIPIENT_OFFICE_CODE": None,
        "SECONDARY_DONOR_CODE": "SD1;SD2",
        "SECONDARY_DONOR": "Secondary One",
    }
    result = GrantSynchronizer._item_save(record)
    assert result == -1


@pytest.mark.django_db
def test_item_save_with_secondary_donors():
    record = {
        "DONOR_CODE": "D002",
        "DONOR_NAME": "Donor Two",
        "GRANT_REF": "GRANT-002",
        "ISSUE_YEAR": "2024",
        "EXPIRY_DATE": None,
        "FINANCIALLY_CLOSE_DATE": None,
        "DESCRIPTION": "Test grant with secondary",
        "USGOV_FLAG": "",
        "THEMATIC": "",
        "EXTERNAL_REF": "",
        "RECIPIENT_OFFICE_CODE": None,
        "SECONDARY_DONOR_CODE": "SD1;SD2",
        "SECONDARY_DONOR": "Secondary One;Secondary Two",
    }
    result = GrantSynchronizer._item_save(record)
    assert result == 1
    assert SecondaryDonor.objects.filter(code="SD1", name="Secondary One").exists()
    assert SecondaryDonor.objects.filter(code="SD2", name="Secondary Two").exists()
    grant = Grant.objects.get(code="GRANT-002")
    assert grant.secondarydonor_set.count() == 2
