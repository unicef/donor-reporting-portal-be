from pathlib import Path

from django.urls import reverse

import pytest
from drf_api_checker.pytest import contract, frozenfixture
from mock import mock
from tests.api_checker import LastModifiedRecorder
from tests.vcrpy import VCR

mocked_a_class = mock.Mock()
mocked_a_instance = mocked_a_class.return_value
mocked_a_instance.acquire_token_for_user.return_value = True


def macioce():
    return True


@frozenfixture()
def site(request, db):
    from tests.factories import SharePointSiteFactory
    return SharePointSiteFactory()


@frozenfixture()
def library(request, db):
    from tests.factories import SharePointLibraryFactory
    return SharePointLibraryFactory()


@contract()
@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/test_sharepoint.yml'))
# @mock.patch.object('donor_reporting_portal.libraries.sharepoint.client.AuthenticationContext', 'acquire_token_for_user', macioce)
@mock.patch.object('donor_reporting_portal.libraries.sharepoint.client.AuthenticationContext', 'acquire_token_for_user', macioce)
def test_sharepoint_list(request, django_app):
    # with mock.patch('donor_reporting_portal.libraries.sharepoint.client.AuthenticationContext') as auth_context:
    # mocked_funct = ''
    # with mock.patch.object(mocked_funct, 'acquire_token_for_user') as mmmm:
    #     mmmm.return_value = True
    #     auth_context.acquire_token_for_user.return_value = True
    return reverse('api:sharepoint-list', kwargs={'site_name': 'TST-SCS-DRP'})


# @contract()
# @VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/macioce.yml'))
# def test_sharepoint_download(request, django_app, logged_user, theme):
#     return reverse('api:sharepoint-download', kwargs={'team_name': 'TST-SCS-DRP', 'filename': 'Macioce'})


@pytest.mark.django_db
@contract(LastModifiedRecorder)
def test_api_sharepoint_libraries(request, django_app, library):
    return reverse('api:sharepoint-library-list')


@pytest.mark.django_db
@contract(LastModifiedRecorder)
def test_api_sharepoint_sites(request, django_app, site):
    return reverse('api:sharepoint-site-list')
