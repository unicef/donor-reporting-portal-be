from unittest import mock
from urllib.parse import urlencode

from django.test import override_settings
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from donor_reporting_portal.api.permissions import is_open_donor
from donor_reporting_portal.api.views.sharepoint import DRPGraphFileDownloadViewSet
from donor_reporting_portal.config.fragments.drp import _source_id


def _request(query_params=None, authenticated=True):
    query = urlencode(query_params or {})
    url = f"/api/graph/Documents/files/test.pdf/download/?{query}"
    request = Request(APIRequestFactory().get(url))
    request.user = mock.Mock(is_authenticated=authenticated, username="user@example.com")
    return request


def _view(request):
    view = DRPGraphFileDownloadViewSet()
    view.request = request
    view.action = "download"
    view.kwargs = {"folder": "Documents", "filename": "test.pdf"}
    return view


def test_source_id_ignores_trailing_comma(monkeypatch):
    monkeypatch.setenv("DRP_SOURCE_ID_THEMATIC_INTERNAL", " 00f6ff72-db3d-42ff-b254-81d9a2548cea , ")
    assert _source_id("DRP_SOURCE_ID_THEMATIC_INTERNAL") == "00f6ff72-db3d-42ff-b254-81d9a2548cea"


def test_source_id_missing(monkeypatch):
    monkeypatch.delenv("DRP_SOURCE_ID_THEMATIC_INTERNAL", raising=False)
    assert _source_id("DRP_SOURCE_ID_THEMATIC_INTERNAL") is None


def test_is_open_donor():
    assert is_open_donor("Various") is True
    assert is_open_donor("D001,Various") is True
    assert is_open_donor("D001") is False
    assert is_open_donor("") is False
    assert is_open_donor(None) is False


def test_download_view_various_donor_is_public():
    assert _view(_request({"donor_code": "Various"})).is_public() is True


@override_settings(DRP_SOURCE_IDS={"internal": "internal-uuid"})
def test_restricted_source_not_public_with_various_donor():
    request = _request({"donor_code": "Various", "source_id": "internal-uuid"})
    assert _view(request).is_public() is False


@override_settings(DRP_SOURCE_IDS={"thematic_internal": "thematic-uuid"})
def test_thematic_source_is_public_without_donor_code():
    request = _request({"source_id": "thematic-uuid"})
    assert _view(request).is_public() is True


@override_settings(DRP_SOURCE_IDS={"thematic_internal": "thematic-uuid"})
def test_authenticated_user_allowed_for_various_donor():
    request = _request({"donor_code": "Various"})
    view = _view(request)
    permission = DRPGraphFileDownloadViewSet.permission_classes[0]()
    assert permission.has_permission(request, view) is True


@override_settings(DRP_SOURCE_IDS={"thematic_internal": "thematic-uuid"})
def test_download_with_various_donor_and_no_source_id():
    request = _request({"donor_code": "Various", "site_id": "site123"})
    view = _view(request)
    client = mock.Mock()
    client.get_drive_id_by_name.return_value = None
    client.download_file.return_value = mock.Mock(
        content=b"pdf", status_code=200, headers={"Content-Type": "application/pdf"}
    )

    with mock.patch("donor_reporting_portal.api.views.sharepoint.get_graph_client", return_value=client):
        response = view.download(request, folder="Documents", filename="test.pdf")

    assert response.status_code == 200
    client.download_file.assert_called_once_with("Documents/test.pdf", drive_id=None, site_id="site123")
