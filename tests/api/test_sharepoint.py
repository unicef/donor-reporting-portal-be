from pathlib import Path

from django.urls import reverse

import pytest
from drf_api_checker.pytest import contract, frozenfixture
from tests.api_checker import LastModifiedRecorder
from tests.factories import DonorFactory, SharePointLibraryFactory, SharePointSiteFactory
from tests.perms import user_grant_role_permission
from tests.vcrpy import VCR


@frozenfixture()
def donor(request, db):
    return DonorFactory(
        name='Australia',
        code='G02701'
    )


@frozenfixture()
def site(request, db):
    return SharePointSiteFactory(
        name='GLB-DRP',
        url='https://asantiagounicef.sharepoint.com/',
        site_type='sites',
        username=None,
        password=None
    )


@frozenfixture()
def library(site, request, db):
    return SharePointLibraryFactory(
        site=site,
        name='2019 Certified Reports'
    )


@pytest.mark.xfail
@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/list.yml'))
@contract()
def test_api(logged_user, library, donor):
    with user_grant_role_permission(logged_user, donor, permissions=['report_metadata.view_donor']):
        url = reverse('api:sharepoint-list', kwargs={'site_name': library.site.name, 'folder_name': library.name})
        data = {'donor_code': donor.code}
        return url, data


@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/caml-list.yml'))
@contract()
def test_api_caml(logged_user, library, donor):
    with user_grant_role_permission(logged_user, donor, permissions=['report_metadata.view_donor']):
        url = reverse('api:sharepoint-caml-list', kwargs={'site_name': library.site.name, 'folder_name': library.name})
        data = {'donor_code': donor.code}
        return url, data


@pytest.mark.django_db
@contract(LastModifiedRecorder)
def test_api_sharepoint_libraries(request, django_app, library):
    return reverse('api:sharepoint-library-list')


@pytest.mark.django_db
@contract(LastModifiedRecorder)
def test_api_sharepoint_sites(request, django_app, site):
    return reverse('api:sharepoint-site-list')
