from pathlib import Path

import pytest

from donor_reporting_portal.apps.report_metadata.models import Donor, ExternalGrant, Grant
from donor_reporting_portal.apps.report_metadata.synchronizers import GrantSynchronizer
from vcrpy import VCR


@pytest.mark.django_db
@VCR.use_cassette(str(Path(__file__).parent / "vcr_cassettes/test_grant_sync.yml"))
def test_grant_sync():
    assert Donor.objects.count() == 0
    assert Grant.objects.count() == 0
    assert ExternalGrant.objects.count() == 0
    GrantSynchronizer().sync()
    assert Donor.objects.count() == 6
    assert Grant.objects.count() == 7
    assert ExternalGrant.objects.count() == 4
