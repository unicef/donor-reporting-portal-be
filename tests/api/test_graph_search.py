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
from donor_reporting_portal.api.views.sharepoint import DRPGraphBasedSearchViewSet, PROPERTY_TO_MANAGED
from sharepoint_rest_api.models import SourceId


@pytest.mark.django_db
class TestDRPGraphBasedSearchViewSet:
    def _make_request(self, method="GET", query_params=None, user=None):
        factory = APIRequestFactory()
        qs = "&".join(f"{k}={v}" for k, v in (query_params or {}).items())
        url = f"/api/graph/search/?{qs}" if qs else "/api/graph/search/"
        wsgi_request = factory.get(url) if method == "GET" else factory.post(url)
        drf_request = Request(wsgi_request)
        if user:
            drf_request.user = user
        return drf_request

    def _make_viewset(self, request):
        view = DRPGraphBasedSearchViewSet()
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

    def test_get_filters_pops_serializer(self):
        view = self._make_viewset(self._make_request())
        result = view.get_filters({"serializer": "gavi", "donor_code": "I49901"})
        assert "serializer" not in result
        assert result == {"donor_code": "I49901"}

    def test_get_selected_default(self):
        request = self._make_request(query_params={"donor_code": "I49901"})
        view = self._make_viewset(request)
        selected = view.get_selected(None)
        assert "Title" in selected
        assert "Author" in selected
        assert "Path" in selected
        assert "Donor" in selected

    def test_get_selected_with_param(self):
        request = self._make_request(query_params={"selected": "Donor,GrantNumber"})
        view = self._make_viewset(request)
        selected = view.get_selected("Donor,GrantNumber")
        assert selected == ["Donor", "GrantNumber", "Title", "Author", "Path"]

    def test_get_selected_gavi(self):
        request = self._make_request(query_params={"serializer": "gavi", "donor_code": "I49901"})
        view = self._make_viewset(request)
        selected = view.get_selected(None)
        assert "Title" in selected
        assert "Donor" in selected
        assert "Number" in selected

    def test_apply_source_id_filters_merges_filters(self):
        SourceId.objects.create(
            source_id="test-uuid",
            default_filters={"filters": {"DRPReportGroup": "Grant"}},
        )
        view = self._make_viewset(self._make_request(query_params={"source_id": "test-uuid"}))
        qp = {"source_id": "test-uuid"}
        view._apply_source_id_filters(qp)
        assert qp["DRPReportGroup"] == "Grant"

    def test_apply_source_id_filters_does_not_overwrite(self):
        SourceId.objects.create(
            source_id="test-uuid",
            default_filters={"filters": {"DRPReportGroup": "Grant"}},
        )
        view = self._make_viewset(self._make_request(query_params={"source_id": "test-uuid"}))
        qp = {"source_id": "test-uuid", "DRPReportGroup": "Thematic"}
        view._apply_source_id_filters(qp)
        assert qp["DRPReportGroup"] == "Thematic"

    def test_apply_source_id_filters_exclude_paths(self):
        SourceId.objects.create(
            source_id="test-uuid",
            default_filters={
                "filters": {},
                "exclude_paths": ["https://example.com/staging/*"],
            },
        )
        view = self._make_viewset(self._make_request(query_params={"source_id": "test-uuid"}))
        qp = {"source_id": "test-uuid"}
        view._apply_source_id_filters(qp)
        assert '-Path:"https://example.com/staging/*"' in qp["search"]

    def test_apply_source_id_filters_search_kql(self):
        SourceId.objects.create(
            source_id="test-uuid",
            default_filters={
                "filters": {},
                "search_kql": "ContentTypeId:0x0101*",
            },
        )
        view = self._make_viewset(self._make_request(query_params={"source_id": "test-uuid"}))
        qp = {"source_id": "test-uuid"}
        view._apply_source_id_filters(qp)
        assert qp["search"] == "ContentTypeId:0x0101*"

    def test_apply_source_id_filters_search_kql_with_existing_search(self):
        SourceId.objects.create(
            source_id="test-uuid",
            default_filters={"filters": {}, "search_kql": "ContentTypeId:0x0101*"},
        )
        view = self._make_viewset(self._make_request(query_params={"source_id": "test-uuid"}))
        qp = {"source_id": "test-uuid", "search": "Donor:I49901"}
        view._apply_source_id_filters(qp)
        assert "ContentTypeId:0x0101*" in qp["search"]
        assert "Donor:I49901" in qp["search"]
        assert "AND" in qp["search"]

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

    def test_map_filter_names_from_property_map(self):
        view = self._make_viewset(self._make_request())
        qp = {"donor_code": "I49901"}
        prop_map = DRPSharePointSearchSerializer.get_property_name_map()
        rev_map = DRPSharePointSearchSerializer.get_property_name_reverse()
        result = view._map_filter_names(qp, prop_map, rev_map)
        assert result == {"Donor": "I49901"}

    def test_map_filter_names_to_camel_fallback(self):
        view = self._make_viewset(self._make_request())
        qp = {"grant_number": "SC130572", "report_generated_by": "smoon"}
        result = view._map_filter_names(qp, {}, {})
        assert result == {"GrantNumber": "SC130572", "ReportGeneratedBy": "smoon"}

    def test_map_filter_names_drp_prefix_stripping(self):
        view = self._make_viewset(self._make_request())
        qp = {"DRPReportGroup": "Grant"}
        result = view._map_filter_names(qp, {}, {})
        assert result == {"ReportGroup": "Grant"}

    def test_map_filter_names_with_not_operator(self):
        view = self._make_viewset(self._make_request())
        qp = {"DRPAwardType__not": "PLF"}
        result = view._map_filter_names(qp, {}, {})
        assert result == {"AwardType__not": "PLF"}

    def test_map_filter_names_skips_control_params(self):
        view = self._make_viewset(self._make_request())
        for name in ("search", "selected", "serializer", "source_id", "page", "order_by"):
            qp = {name: "value"}
            result = view._map_filter_names(qp, {}, {})
            assert result == {}, f"Failed for {name}"

    def test_map_filter_names_rev_inv_lookup(self):
        view = self._make_viewset(self._make_request())
        qp = {"DonorCode": "I49901"}
        rev_map = {"DonorCode": "DRPDonorCode"}
        result = view._map_filter_names(qp, {}, rev_map)
        assert result == {"DonorCode": "I49901"}

    @override_settings(DRP_SOURCE_IDS={"internal": "test-uuid"})
    def test_get_queryset_calls_search(self):
        request = self._make_request(query_params={"donor_code": "I49901"})
        view = self._make_viewset(request)
        mock_client = mock.Mock()
        mock_client.search.return_value = ([], 0)
        view.client = mock_client
        result = view.get_queryset()
        mock_client.search.assert_called_once()
        call_kwargs = mock_client.search.call_args[1]
        assert call_kwargs["search"] is None
        assert call_kwargs["filters"] == {"Donor": "I49901"}
        assert call_kwargs["page"] == 1
        assert call_kwargs["searchable_properties"] == set(PROPERTY_TO_MANAGED.values())
        assert result == []

    @override_settings(DRP_SOURCE_IDS={"internal": "test-uuid"})
    def test_get_queryset_with_search_param(self):
        request = self._make_request(query_params={"donor_code": "I49901", "search": "test"})
        view = self._make_viewset(request)
        mock_client = mock.Mock()
        mock_client.search.return_value = ([], 0)
        view.client = mock_client
        view.get_queryset()
        call_kwargs = mock_client.search.call_args[1]
        assert call_kwargs["search"] == "test"

    @override_settings(DRP_SOURCE_IDS={"internal": "test-uuid"})
    def test_get_queryset_with_extra_filters(self):
        request = self._make_request(
            query_params={
                "donor_code": "I49901",
                "grant_number": "SC130572",
                "report_generated_by": "smoon",
            }
        )
        view = self._make_viewset(request)
        mock_client = mock.Mock()
        mock_client.search.return_value = ([], 0)
        view.client = mock_client
        view.get_queryset()
        call_kwargs = mock_client.search.call_args[1]
        assert call_kwargs["filters"]["RefinableString161"] == "SC130572"
        assert call_kwargs["filters"]["RefinableString174"] == "smoon"
