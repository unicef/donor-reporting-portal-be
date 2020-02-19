from pathlib import Path
from unittest import mock

from drf_api_checker.pytest import frozenfixture
from pytest import fixture
from tests.factories import SharePointLibraryFactory, SharePointSiteFactory, SharePointTenantFactory
from tests.vcrpy import VCR

from donor_reporting_portal.libraries.sharepoint.client import SharePointClient


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


@fixture()
def sh_client(library, request, db):
    dl_info = {
        'url': library.site.site_url(),
        'relative_url': library.site.relative_url(),
        'folder': library.name
    }
    return SharePointClient(**dl_info)


# to regenerate cassettes
# comment the mock_client fixture (since is mocking the login)
@fixture(scope='session', autouse=True)
def mock_client():
    patcher = mock.patch('donor_reporting_portal.libraries.sharepoint.client.AuthenticationContext')
    my_mock = patcher.start()
    my_mock.acquire_token_for_user.return_value = True
    yield
    patcher.stop()  # not needed just for clarity


@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/folders.yml'))
def test_folders(library, sh_client, mock_client):
    items = sh_client.read_folders(library.name)
    assert len(items) == 31


@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/items.yml'))
def test_items(sh_client, mock_client):
    items = sh_client.read_items()
    assert len(items) == 220


@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/caml_items.yml'))
def test_caml_items(sh_client, mock_client):
    items = sh_client.read_caml_items()
    assert len(items) == 220


@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/files.yml'))
def test_files(sh_client, mock_client):
    items = sh_client.read_files()
    assert len(items) == 220


@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/file.yml'))
def test_file(sh_client, mock_client):
    my_file = sh_client.read_file('CertifiedDonorStatement_CSACC_KC120003_31122019.pdf')
    assert my_file.properties['Name'] == 'CertifiedDonorStatement_CSACC_KC120003_31122019.pdf'


# @VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/download.yml'))
# def test_download(sh_client):
#     my_file = sh_client.download_file('CertifiedDonorStatement_SC110743_31122018')
#     assert my_file.properties['Name'] == 'CertifiedDonorStatement_SC110743_31122018.pdf'
