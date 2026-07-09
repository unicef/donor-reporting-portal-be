from datetime import datetime
from unittest import mock

from django.test import override_settings

import pytest
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from donor_reporting_portal.api.serializers.sharepoint import (
    DRPSharePointSearchSerializer,
    GaviSharePointSearchSerializer,
    GaviSoaSharePointSearchSerializer,
)
from donor_reporting_portal.api.views.sharepoint import (
    DRPSharepointSearchViewSet,
    DRPSharePointUrlFileViewSet,
    DRPSharePointSettingsFileViewSet,
    DRPSharePointSettingsRestViewSet,
    DRPSharePointSettingsCamlViewSet,
    DRPSharePointUrlRestViewSet,
    DRPSharePointUrlCamlViewSet,
    DRPSharePointSettingsSearchViewSet,
    DRPSharePointUrlSearchViewSet,
    SharePointGroupViewSet,
    DRPGraphClient,
)
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
        from donor_reporting_portal.api.serializers.sharepoint import DRPSerializerMixin

        with mock.patch("donor_reporting_portal.api.serializers.sharepoint.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 6, 30, 12, 0, 0)
            serializer = DRPSerializerMixin()
            obj = {"Modified": "2026-06-28T10:00:00"}
            assert serializer.get_is_new(obj) is True

    def test_get_is_new_no_modified(self):
        from donor_reporting_portal.api.serializers.sharepoint import DRPSerializerMixin

        serializer = DRPSerializerMixin()
        obj = {}
        assert serializer.get_is_new(obj) is False

    def test_get_download_url_base(self):
        from donor_reporting_portal.api.serializers.sharepoint import DRPSerializerMixin

        serializer = DRPSerializerMixin()
        with mock.patch(
            "sharepoint_rest_api.serializers.sharepoint.SharePointUrlSerializer.get_download_url",
            return_value="https://example.com/doc.pdf",
        ):
            obj = {"DonorCode": "I49901"}
            url = serializer.get_download_url(obj)
            assert "donor_code=I49901" in url


class TestSharePointGroupViewSet:
    def test_viewset_attributes(self):
        assert SharePointGroupViewSet.queryset is not None
        assert SharePointGroupViewSet.serializer_class is not None


class TestDRPViewSetSubclasses:
    def test_settings_rest(self):
        assert DRPSharePointSettingsRestViewSet.serializer_class is not None

    def test_settings_caml(self):
        assert DRPSharePointSettingsCamlViewSet.serializer_class is not None

    def test_url_rest(self):
        assert DRPSharePointUrlRestViewSet.serializer_class is not None

    def test_url_caml(self):
        assert DRPSharePointUrlCamlViewSet.serializer_class is not None

    def test_url_file(self):
        assert DRPSharePointUrlFileViewSet.permission_classes is not None

    def test_settings_file(self):
        assert DRPSharePointSettingsFileViewSet.permission_classes is not None

    def test_settings_search(self):
        assert DRPSharePointSettingsSearchViewSet is not None

    def test_url_search(self):
        assert DRPSharePointUrlSearchViewSet is not None


class TestDRPGraphClient:
    def test_graph_client_subclass(self):
        assert issubclass(DRPGraphClient, mock.ANY)  # pragma: no cover
