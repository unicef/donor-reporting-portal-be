from datetime import datetime
from unittest import mock

from django.test import override_settings

import pytest
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from donor_reporting_portal.api.serializers.sharepoint import (
    DRPSerializerMixin,
    DRPSharePointBaseSerializer,
    DRPSharePointSearchSerializer,
    GaviSharePointSearchSerializer,
    GaviSoaSharePointSearchSerializer,
)
from donor_reporting_portal.api.views.sharepoint import (
    DRPSharepointSearchViewSet,
    DRPGraphBasedSearchViewSet,
    SharePointGroupViewSet,
    DRPGraphClient,
)
from sharepoint_rest_api.graph_client import GraphClient
from sharepoint_rest_api.models import SourceId


@pytest.mark.django_db
class TestDRPSharepointSearchViewSet:
    def _make_request(self, method="GET", query_params=None, user=None):
        factory = APIRequestFactory()
        qs = "&".join(f"{k}={v}" for k, v in (query_params or {}).items())
        url = f"/api/sharepoint/search/?{qs}" if qs else "/api/sharepoint/search/"
        wsgi_request = factory.get(url) if method == "GET" else factory.post(url)
        drf_request = Request(wsgi_request)
        if user:
            drf_request.user = user
        return drf_request

    def _make_viewset(self, request):
        view = DRPSharepointSearchViewSet()
        view.request = request
        view.action = "list"
        view.format_kwarg = None
        return view

    def test_get_serializer_class_default(self):
        request = self._make_request(query_params={"donor_code": "I49901"})
        view = self._make_viewset(request)
        assert view.get_serializer_class() == DRPSharePointSearchSerializer

    def test_get_serializer_class_gavi(self):
        request = self._make_request(query_params={"serializer": "gavi", "donor_code": "I49901"})
        view = self._make_viewset(request)
        assert view.get_serializer_class() == GaviSharePointSearchSerializer

    def test_get_serializer_class_soa(self):
        request = self._make_request(query_params={"serializer": "soa", "donor_code": "I49901"})
        view = self._make_viewset(request)
        assert view.get_serializer_class() == GaviSoaSharePointSearchSerializer

    def test_get_selected_default(self):
        request = self._make_request(query_params={"donor_code": "I49901"})
        view = self._make_viewset(request)
        selected = view.get_selected(None)
        assert "Title" in selected
        assert "Donor" in selected

    def test_get_selected_with_param(self):
        request = self._make_request(query_params={"selected": "Donor,GrantNumber"})
        view = self._make_viewset(request)
        selected = view.get_selected("Donor,GrantNumber")
        assert selected == ["Donor", "GrantNumber", "Title", "Author", "Path"]

    def test_get_filters_basic(self):
        request = self._make_request(query_params={"donor_code": "I49901"})
        view = self._make_viewset(request)
        result = view.get_filters({"serializer": "gavi", "donor_code": "I49901"})
        assert "serializer" not in result
        assert result["DRPDonor"] == "I49901"

    def test_get_filters_ctn_field(self):
        request = self._make_request(query_params={"number": "CTN123"})
        view = self._make_viewset(request)
        view.prefix = "DRP"
        result = view.get_filters({"serializer": "gavi", "number": "CTN123"})
        assert "CTNNumber" in result

    def test_get_filters_with_operator(self):
        request = self._make_request(query_params={})
        view = self._make_viewset(request)
        result = view.get_filters({"donor_code__in": "I49901,I49902"})
        assert result == {"DRPDonor__in": "I49901,I49902"}

    def test_get_filters_unknown_field(self):
        request = self._make_request(query_params={})
        view = self._make_viewset(request)
        result = view.get_filters({"unknown_field": "value"})
        assert result == {"unknown_field": "value"}

    def test_apply_source_id_filters_none(self):
        view = self._make_viewset(self._make_request())
        qp = {}
        view._apply_source_id_filters(qp)
        assert qp == {}

    def test_apply_source_id_filters_not_found(self):
        view = self._make_viewset(self._make_request(query_params={"source_id": "nonexistent"}))
        qp = {"source_id": "nonexistent"}
        view._apply_source_id_filters(qp)
        assert qp == {"source_id": "nonexistent", "order_by": "DRPMODIFIED desc"}

    def test_apply_source_id_filters_with_order_by(self):
        SourceId.objects.create(
            source_id="test-uuid",
            default_filters={"order_by": "Donor asc"},
        )
        view = self._make_viewset(self._make_request(query_params={"source_id": "test-uuid"}))
        qp = {"source_id": "test-uuid"}
        view._apply_source_id_filters(qp)
        assert qp["order_by"] == "Donor asc"

    def test_apply_source_id_filters_existing_order_by(self):
        SourceId.objects.create(
            source_id="test-uuid",
            default_filters={"order_by": "Donor asc"},
        )
        view = self._make_viewset(self._make_request(query_params={"source_id": "test-uuid"}))
        qp = {"source_id": "test-uuid", "order_by": "Modified desc"}
        view._apply_source_id_filters(qp)
        assert qp["order_by"] == "Modified desc"

    def test_is_public_thematic_internal(self):
        SourceId.objects.create(source_id="thematic-int")
        request = self._make_request(query_params={"source_id": "thematic-int"})
        request.user = mock.Mock()
        request.user.username = "user@unicef.org"
        view = self._make_viewset(request)
        with override_settings(DRP_SOURCE_IDS={"thematic_internal": "thematic-int"}):
            assert view.is_public() is True

    def test_is_public_thematic_external(self):
        SourceId.objects.create(source_id="thematic-ext")
        request = self._make_request(query_params={"source_id": "thematic-ext"})
        request.user = mock.Mock()
        request.user.username = "user@example.com"
        view = self._make_viewset(request)
        with override_settings(DRP_SOURCE_IDS={"thematic_external": "thematic-ext"}):
            assert view.is_public() is True

    def test_is_public_internal_unicef(self):
        SourceId.objects.create(source_id="int-uuid")
        request = self._make_request(query_params={"source_id": "int-uuid"})
        request.user = mock.Mock()
        request.user.username = "user@unicef.org"
        view = self._make_viewset(request)
        with override_settings(DRP_SOURCE_IDS={"internal": "int-uuid", "pool_internal": "other"}):
            assert view.is_public() is True

    def test_is_public_non_unicef_denied(self):
        SourceId.objects.create(source_id="int-uuid")
        request = self._make_request(query_params={"source_id": "int-uuid"})
        request.user = mock.Mock()
        request.user.username = "user@example.com"
        view = self._make_viewset(request)
        with override_settings(DRP_SOURCE_IDS={"internal": "int-uuid"}):
            assert view.is_public() is False


@pytest.mark.django_db
class TestDRPSharePointBaseSerializer:
    def test_get_is_new_with_modified(self):
        with mock.patch("donor_reporting_portal.api.serializers.sharepoint.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 6, 30, 12, 0, 0)
            serializer = DRPSerializerMixin()
            obj = {"Modified": "2026-06-28T10:00:00"}
            assert serializer.get_is_new(obj) is True

    def test_get_is_new_no_modified(self):
        serializer = DRPSerializerMixin()
        obj = {}
        assert serializer.get_is_new(obj) is False

    @override_settings(HOST="http://localhost:8000")
    def test_get_download_url_base(self):
        serializer = DRPSerializerMixin(context={"folder": "Shared Documents"})
        obj = {"FileLeafRef": "report.pdf", "DonorCode": "I49901"}
        url = serializer.get_download_url(obj)
        assert "http://localhost:8000/api/graph/" in url
        assert "report.pdf/download/" in url
        assert "donor_code=I49901" in url


class TestSharePointGroupViewSet:
    def test_viewset_attributes(self):
        assert SharePointGroupViewSet.queryset is not None
        assert SharePointGroupViewSet.serializer_class is not None


class TestDRPGraphClient:
    def test_graph_client_subclass(self):
        assert issubclass(DRPGraphClient, GraphClient)  # pragma: no cover


@pytest.mark.django_db
class TestDRPGraphBasedSearchViewSetIsPublic:
    def _make_request(self, query_params=None):
        factory = APIRequestFactory()
        qs = "&".join(f"{k}={v}" for k, v in (query_params or {}).items())
        url = f"/api/graph/search/?{qs}" if qs else "/api/graph/search/"
        wsgi_request = factory.get(url)
        return Request(wsgi_request)

    def _make_viewset(self, request):
        view = DRPGraphBasedSearchViewSet()
        view.request = request
        view.action = "list"
        view.format_kwarg = None
        return view

    @override_settings(DRP_SOURCE_IDS={"thematic_internal": "thematic-int"})
    def test_is_public_thematic_internal(self):
        request = self._make_request(query_params={"source_id": "thematic-int"})
        request.user = mock.Mock()
        request.user.username = "user@unicef.org"
        view = self._make_viewset(request)
        assert view.is_public() is True

    @override_settings(DRP_SOURCE_IDS={"thematic_external": "thematic-ext"})
    def test_is_public_thematic_external(self):
        request = self._make_request(query_params={"source_id": "thematic-ext"})
        request.user = mock.Mock()
        request.user.username = "user@example.com"
        view = self._make_viewset(request)
        assert view.is_public() is True

    @override_settings(DRP_SOURCE_IDS={"internal": "int-uuid", "pool_internal": "other"})
    def test_is_public_internal_unicef(self):
        request = self._make_request(query_params={"source_id": "int-uuid"})
        request.user = mock.Mock()
        request.user.username = "user@unicef.org"
        view = self._make_viewset(request)
        assert view.is_public() is True

    @override_settings(DRP_SOURCE_IDS={"internal": "int-uuid"})
    def test_is_public_non_unicef_denied(self):
        request = self._make_request(query_params={"source_id": "int-uuid"})
        request.user = mock.Mock()
        request.user.username = "user@example.com"
        view = self._make_viewset(request)
        assert view.is_public() is False

    @override_settings(DRP_SOURCE_IDS={"thematic_internal": "thematic-int", "thematic_external": "thematic-ext"})
    def test_is_public_no_source_id(self):
        request = self._make_request()
        request.user = mock.Mock()
        request.user.username = "user@example.com"
        view = self._make_viewset(request)
        assert view.is_public() is False


class TestDRPSharePointBaseSerializerDownloadUrl:
    @override_settings(HOST="http://localhost:8000")
    def test_get_download_url_backend_proxied(self):
        serializer = DRPSharePointBaseSerializer()
        obj = {
            "Path": "https://unitst.sharepoint.com/sites/GLB-DRP/Shared%20Documents/file.pdf",
            "DRPDonorCode": "I49901",
            "SiteId": "site123",
            "DriveId": "drive456",
            "DocId": "item789",
        }
        url = serializer.get_download_url(obj)
        assert "http://localhost:8000/api/graph/" in url
        assert "file.pdf/download/" in url
        assert "donor_code=I49901" in url
        assert "site_id=site123" in url
        assert "drive_id=drive456" in url
        assert "item_id=item789" in url

    @override_settings(HOST="http://localhost:8000")
    def test_get_download_url_no_donor_code(self):
        serializer = DRPSharePointBaseSerializer()
        obj = {
            "Path": "https://unitst.sharepoint.com/sites/GLB-DRP/Shared%20Documents/file.pdf",
            "SiteId": "site123",
            "DriveId": "drive456",
            "DocId": "item789",
        }
        url = serializer.get_download_url(obj)
        assert "http://localhost:8000/api/graph/" in url
        assert "file.pdf/download/" in url
        assert "donor_code" not in url
        assert "site_id=site123" in url
        assert "drive_id=drive456" in url
        assert "item_id=item789" in url

    @override_settings(HOST="http://localhost:8000")
    def test_get_download_url_no_site_id(self):
        serializer = DRPSharePointBaseSerializer()
        obj = {
            "Path": "https://unitst.sharepoint.com/sites/GLB-DRP/Shared%20Documents/file.pdf",
        }
        url = serializer.get_download_url(obj)
        assert url is None

    def test_get_download_url_no_path(self):
        serializer = DRPSharePointBaseSerializer()
        obj = {"DRPDonorCode": "I49901"}
        assert serializer.get_download_url(obj) is None

    def test_get_download_url_empty_path(self):
        serializer = DRPSharePointBaseSerializer()
        obj = {"Path": "", "DRPDonorCode": "I49901"}
        assert serializer.get_download_url(obj) is None

    def test_extract_site_relative_path_full_url(self):
        path = DRPSharePointBaseSerializer._extract_site_relative_path(
            "https://unitst.sharepoint.com/sites/GLB-DRP/Shared%20Documents/file.pdf"
        )
        assert path == "Shared Documents/file.pdf"

    def test_extract_site_relative_path_server_relative(self):
        path = DRPSharePointBaseSerializer._extract_site_relative_path("/sites/GLB-DRP/Shared%20Documents/file.pdf")
        assert path == "Shared Documents/file.pdf"

    def test_extract_site_relative_path_nested_folder(self):
        path = DRPSharePointBaseSerializer._extract_site_relative_path(
            "https://unitst.sharepoint.com/sites/GLB-DRP/Shared%20Documents/Subfolder/file.pdf"
        )
        assert path == "Shared Documents/Subfolder/file.pdf"

    def test_extract_site_relative_path_no_match(self):
        path = DRPSharePointBaseSerializer._extract_site_relative_path("https://example.com/other/path/file.pdf")
        assert path == "path/file.pdf"

    @override_settings(HOST="http://localhost:8000")
    def test_get_download_url_donor_code_semicolon(self):
        serializer = DRPSharePointBaseSerializer()
        obj = {
            "Path": "https://unitst.sharepoint.com/sites/GLB-DRP/Shared%20Documents/file.pdf",
            "DRPDonorCode": "I49901;I49902",
            "SiteId": "site123",
        }
        url = serializer.get_download_url(obj)
        assert "donor_code=I49901,I49902" in url

    @override_settings(HOST="http://localhost:8000")
    def test_get_download_url_subfolder(self):
        serializer = DRPSharePointBaseSerializer()
        obj = {
            "Path": "https://unitst.sharepoint.com/sites/GLB-DRP/Shared%20Documents/Subfolder/nested%20file.pdf",
            "DRPDonorCode": "G01001",
            "SiteId": "site123",
        }
        url = serializer.get_download_url(obj)
        assert "Subfolder" in url
        assert "/api/graph/" in url
        assert "nested%20file.pdf/download/" in url
        assert "donor_code=G01001" in url
