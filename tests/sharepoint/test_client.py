from pathlib import Path

from drf_api_checker.pytest import frozenfixture
from pytest import fixture
from tests.vcrpy import VCR

from donor_reporting_portal.libraries.sharepoint.client import SharePointClient


@frozenfixture()
def site(request, db, SharePointSiteFactory=None):
    from tests.factories import SharePointSiteFactory
    return SharePointSiteFactory(
        name='GLB-DRP',
        url='https://asantiagounicef.sharepoint.com/',
        site_type='sites'
    )


@frozenfixture()
def library(site, request, db):
    from tests.factories import SharePointLibraryFactory
    return SharePointLibraryFactory(
        site=site,
        name='2019 Certified Reports'
    )


@fixture()
def sh_client(library, request, db):
    dl_info = {
        'url': library.site.site_url(),
        'relative_url': library.site.relative_url(),
        'folder_name': library.name
    }
    return SharePointClient(**dl_info)


@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/folders.yml'))
def test_folders(library, sh_client):
    items = sh_client.read_folders(library.name)
    assert len(items) == 31


@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/items.yml'))
def test_items(sh_client):
    items = sh_client.read_items()
    assert len(items) == 15


@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/caml_items.yml'))
def test_caml_items(sh_client):
    items = sh_client.read_caml_items()
    assert len(items) == 15


@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/files.yml'))
def test_files(sh_client):
    items = sh_client.read_files()
    assert len(items) == 15


@VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/file.yml'))
def test_file(sh_client):
    my_file = sh_client.read_file('CertifiedDonorStatement_SC110743_31122018')
    assert my_file.properties['Name'] == 'CertifiedDonorStatement_SC110743_31122018.pdf'


# @VCR.use_cassette(str(Path(__file__).parent / 'vcr_cassettes/download.yml'))
# def test_download(sh_client):
#     my_file = sh_client.download_file('CertifiedDonorStatement_SC110743_31122018')
#     assert my_file.properties['Name'] == 'CertifiedDonorStatement_SC110743_31122018.pdf'
