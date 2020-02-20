from pathlib import Path

from django.urls import reverse

from drf_api_checker.pytest import api_checker_datadir, contract, frozenfixture  # noqa
from drf_api_checker.recorder import Recorder
from tests.factories import DonorFactory, SharePointLibraryFactory, SharePointSiteFactory, SharePointTenantFactory
from tests.perms import user_grant_role_permission
from tests.vcrpy import VCR


@frozenfixture()
def donor(request, db):
    return DonorFactory(
        name='Australia',
        code='G02701'
    )


@frozenfixture()
def tenant(request, db):
    return SharePointTenantFactory(
        url='https://unitst.sharepoint.com/',
        username=None,
        password=None
    )


@frozenfixture()
def site(tenant, request, db):
    return SharePointSiteFactory(
        tenant=tenant,
        name='GLB-DRP',
        site_type='sites',
    )


@frozenfixture()
def library(site, request, db):
    return SharePointLibraryFactory(
        site=site,
        name='2019 Certified Reports'
    )


@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/list.yml'))
def test_api(api_checker_datadir, logged_user, library, donor):
    url = reverse('api:sharepoint-list',
                  kwargs={'tenant': library.site.tenant.name, 'site': library.site.name, 'folder': library.name})
    data = {'donor_code': donor.code}
    with user_grant_role_permission(logged_user, donor, permissions=['report_metadata.view_donor']):
        recorder = Recorder(api_checker_datadir, as_user=logged_user)
        recorder.assertGET(url, data=data)


@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/caml-list.yml'))
def test_api_caml(api_checker_datadir, logged_user, library, donor):
    url = reverse('api:sharepoint-caml-list',
                  kwargs={'tenant': library.site.tenant.name, 'site': library.site.name, 'folder': library.name})
    data = {'donor_code': donor.code}
    with user_grant_role_permission(logged_user, donor, permissions=['report_metadata.view_donor']):
        recorder = Recorder(api_checker_datadir, as_user=logged_user)
        recorder.assertGET(url, data=data)
