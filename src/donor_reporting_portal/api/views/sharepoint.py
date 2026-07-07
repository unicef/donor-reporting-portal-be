import csv

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.utils.functional import cached_property

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from sharepoint_rest_api import config as sp_config
from sharepoint_rest_api.config import SHAREPOINT_PAGE_SIZE
from sharepoint_rest_api.graph_client import GraphClient, GraphClientError
from sharepoint_rest_api.utils import to_camel
from sharepoint_rest_api.views.base import SharePointSearchViewSet
from sharepoint_rest_api.views.graph_based import GraphBasedSearchViewSet
from sharepoint_rest_api.views.settings_based import (
    SharePointSettingsCamlViewSet,
    SharePointSettingsFileViewSet,
    SharePointSettingsRestViewSet,
    SharePointSettingsSearchViewSet,
)
from sharepoint_rest_api.views.url_based import (
    SharePointUrlCamlViewSet,
    SharePointUrlFileViewSet,
    SharePointUrlRestViewSet,
    SharePointUrlSearchViewSet,
)

from donor_reporting_portal.api.permissions import DonorPermission, PublicLibraryPermission
from donor_reporting_portal.api.serializers.fields import (
    CTNSearchMultiSharePointField,
    CTNSearchSharePointField,
    DRPSearchSharePointField,
)
from donor_reporting_portal.api.serializers.sharepoint import (
    DRPSharePointSearchSerializer,
    DRPSharePointSettingsSerializer,
    DRPSharePointUrlSerializer,
    GaviSharePointSearchSerializer,
    GaviSoaSharePointSearchSerializer,
    SharePointGroupSerializer,
)
from sharepoint_rest_api.models import SourceId
from donor_reporting_portal.apps.sharepoint.models import SharePointGroup


class SharePointGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SharePointGroup.objects.all()
    serializer_class = SharePointGroupSerializer


class DRPViewSet:
    permission_classes = ((DonorPermission | PublicLibraryPermission),)


class DRPSharePointSettingsRestViewSet(DRPViewSet, SharePointSettingsRestViewSet):
    serializer_class = DRPSharePointSettingsSerializer


class DRPSharePointSettingsCamlViewSet(DRPViewSet, SharePointSettingsCamlViewSet):
    serializer_class = DRPSharePointSettingsSerializer


class DRPSharePointUrlRestViewSet(DRPViewSet, SharePointUrlRestViewSet):
    serializer_class = DRPSharePointUrlSerializer


class DRPSharePointUrlCamlViewSet(DRPViewSet, SharePointUrlCamlViewSet):
    serializer_class = DRPSharePointUrlSerializer


class DRPSharePointUrlFileViewSet(SharePointUrlFileViewSet):
    permission_classes = (DonorPermission,)


class DRPSharePointSettingsFileViewSet(SharePointSettingsFileViewSet):
    permission_classes = (DonorPermission,)


class DRPSharepointSearchViewSet(SharePointSearchViewSet):
    prefix = "DRP"
    serializer_class = DRPSharePointSearchSerializer

    def get_serializer_class(self):
        query_params = self.request.query_params
        if query_params.get("serializer") == "gavi":
            return GaviSharePointSearchSerializer
        if query_params.get("serializer") == "soa":
            return GaviSoaSharePointSearchSerializer
        return super().get_serializer_class()

    def is_public(self):
        """Check if the source id is public or restricted to UNICEF users."""
        source_id = self.request.query_params.get("source_id", None)
        public = source_id in [
            settings.DRP_SOURCE_IDS["thematic_internal"],
            settings.DRP_SOURCE_IDS["thematic_external"],
        ]
        if public:
            return True
        unicef_user = self.request.user.username.endswith("@unicef.org")
        return unicef_user and source_id in [
            settings.DRP_SOURCE_IDS["internal"],
            settings.DRP_SOURCE_IDS["pool_internal"],
        ]

    def get_selected(self, selected):
        def to_drp(source, value):
            prefix = "CTN" if isinstance(value, CTNSearchSharePointField | CTNSearchMultiSharePointField) else "DRP"
            return prefix + to_camel(source)

        autofields = [to_drp(key, value) for key, value in self.get_serializer_class()._declared_fields.items()]
        selected = selected.split(",") if selected else autofields
        return selected + ["Title", "Author", "Path"]

    def get_filters(self, kwargs):
        # we can enforce filters here
        kwargs.pop("serializer", None)
        new_kwargs = {}
        drp_fields = [
            key
            for key, value in self.get_serializer_class()._declared_fields.items()
            if isinstance(value, DRPSearchSharePointField)
        ]

        ctn_fields = [
            key
            for key, value in self.get_serializer_class()._declared_fields.items()
            if isinstance(value, CTNSearchSharePointField)
        ]

        for key, value in kwargs.items():
            key_splits = key.split("__")
            filter_name = key_splits[0]
            filter_type = key_splits[-1] if len(key_splits) > 1 else None
            if filter_name in drp_fields:
                new_key = self.prefix + to_camel(filter_name)
                if filter_type:
                    new_key = f"{new_key}__{filter_type}"
                new_kwargs[new_key] = value
            elif filter_name in ctn_fields:
                new_key = "CTN" + to_camel(filter_name)
                if filter_type:
                    new_key = f"{new_key}__{filter_type}"
                new_kwargs[new_key] = value
            else:
                new_kwargs[key] = value

        return new_kwargs

    def _apply_source_id_filters(self, qp):
        source_id = qp.get("source_id")
        if not source_id:
            return
        try:
            source_obj = SourceId.objects.get(source_id=source_id)
            default_filters = source_obj.default_filters or {}
        except SourceId.DoesNotExist:
            default_filters = {}
        for key, value in default_filters.get("filters", {}).items():
            if key not in qp:
                qp[key] = value
        search_kql = default_filters.get("search_kql", "")
        if search_kql:
            existing_search = qp.get("search", "")
            if existing_search:
                qp["search"] = f"({search_kql}) AND ({existing_search})"
            else:
                qp["search"] = search_kql
        exclude_paths = default_filters.get("exclude_paths", [])
        if exclude_paths:
            path_exclusions = " ".join(f'-Path:"{p}"' for p in exclude_paths)
            qp["search"] = f"{path_exclusions} {qp.get('search', '')}".strip()
        order_by = default_filters.get("order_by")
        if order_by and "order_by" not in qp:
            qp["order_by"] = order_by
        elif "order_by" not in qp:
            qp["order_by"] = "LastModifiedTime desc"

    def get_queryset(self, **kwargs):
        qp = self.request.query_params.copy()
        self._apply_source_id_filters(qp)
        qp.update(kwargs)
        kwargs = qp
        return super().get_queryset(**kwargs)

    @action(detail=False, methods=["get"])
    def export(self, request, *args, **kwargs):
        exit_condition = True
        response = HttpResponse(content_type="text/csv")
        filename = f"drp_export_{timezone.now().date()}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        headers = self.get_serializer_class().export_headers
        writer = csv.writer(response)
        page = 1
        qs = self.get_queryset(page=page)
        writer.writerow([key.replace("CTN", "") for key in qs[0] if key in headers])
        while exit_condition:
            for row in qs:
                writer.writerow([str(value) for key, value in row.items() if key in headers])
            exit_condition = page * SHAREPOINT_PAGE_SIZE < self.total_rows
            page += 1
            qs = self.get_queryset(page=page)
        return response


class DRPSharePointSettingsSearchViewSet(DRPViewSet, DRPSharepointSearchViewSet, SharePointSettingsSearchViewSet):
    """DRP Search Viewset for settings based."""


class DRPSharePointUrlSearchViewSet(DRPViewSet, DRPSharepointSearchViewSet, SharePointUrlSearchViewSet):
    """DRP Search Viewset for url based."""


class DRPGraphBasedSearchViewSet(DRPViewSet, GraphBasedSearchViewSet):
    """DRP Search Viewset for graph based.

    Uses Graph Search API with KQL. Property name mapping is derived
    dynamically from the serializer's field definitions, not from a
    hardcoded map. The viewset builds the mapping and passes already-mapped
    managed property names to GraphClient.
    """

    serializer_class = DRPSharePointSearchSerializer
    _PROPERTY_TO_KQL = {
        "Donor": "Donor",
        "GrantNumber": "RefinableString161",
        "ReportGroup": "RefinableString164",
        "ReportStatus": "RefinableString166",
        "AwardType": "RefinableString176",
        "Retracted": "RefinableString173",
        "Created": "RefinableDate09",
        "Modified": "RefinableDate11",
        "GrantExpiryDate": "RefinableDate14",
        "ReportEndDate": "RefinableDate15",
        "DonorDocument": "RefinableString163",
        "DonorReportCategory": "RefinableString171",
        "ExternalReference": "RefinableString168",
        "FrameworkAgreement": "RefinableString162",
        "GrantIssueYear": "RefinableString167",
        "RecipientOffice": "RefinableString165",
        "ReportGeneratedBy": "RefinableString174",
        "ReportMethod": "RefinableString172",
        "ReportType": "RefinableString169",
        "Theme": "RefinableString170",
        "DonorCode": "RefinableString175",
    }

    def get_serializer_class(self):
        query_params = self.request.query_params
        if query_params.get("serializer") == "gavi":
            return GaviSharePointSearchSerializer
        if query_params.get("serializer") == "soa":
            return GaviSoaSharePointSearchSerializer
        return super().get_serializer_class()

    def get_filters(self, kwargs):
        kwargs.pop("serializer", None)
        return kwargs

    def get_selected(self, selected):
        serializer_class = self.get_serializer_class()
        autofields = []
        for name, field in serializer_class._declared_fields.items():
            if hasattr(field, "get_search_property"):
                prop = field.get_search_property()
                autofields.append(prop if prop is not None else to_camel(name))
            else:
                autofields.append(to_camel(name))
        selected = selected.split(",") if selected else autofields
        return selected + ["Title", "Author", "Path"]

    def _map_filter_names(self, qp, property_name_map, reverse_map):
        mapped_filters = {}
        for name, value in qp.items():
            if name in ("search", "selected", "serializer", "source_id", "page", "order_by"):
                continue
            parts = name.split("__")
            raw_name = parts[0]
            operator_key = f"__{parts[-1]}" if len(parts) > 1 else ""
            if raw_name in property_name_map:
                mapped_name = property_name_map[raw_name]
            elif "_" in raw_name:
                mapped_name = to_camel(raw_name)
            else:
                mapped_name = raw_name
                if reverse_map:
                    rev_inv = {v: k for k, v in reverse_map.items()}
                    mapped_name = rev_inv.get(raw_name, raw_name)
                if mapped_name == raw_name:
                    for prefix in ("DRP", "CTN", "GAVI"):
                        if raw_name.startswith(prefix):
                            stripped = raw_name[len(prefix) :]
                            if stripped:
                                mapped_name = stripped
                                break
            mapped_filters[f"{mapped_name}{operator_key}"] = value
        return mapped_filters

    @cached_property
    def client(self):
        try:
            return DRPGraphClient(
                url=f"{sp_config.SHAREPOINT_TENANT}/{sp_config.SHAREPOINT_SITE_TYPE}/{sp_config.SHAREPOINT_SITE}",
                relative_url=f"{sp_config.SHAREPOINT_SITE_TYPE}/{sp_config.SHAREPOINT_SITE}",
                folder=self.folder,
            )
        except GraphClientError:
            raise PermissionDenied

    def get_queryset(self, **kwargs):
        qp = self.request.query_params.dict()
        qp.setdefault("order_by", "DRPMODIFIED desc")
        self._apply_source_id_filters(qp)
        qp.update(kwargs)

        serializer_class = self.get_serializer_class()
        property_name_map = serializer_class.get_property_name_map()
        reverse_map = serializer_class.get_property_name_reverse()

        search = qp.get("search")
        page = int(qp.get("page", 1))
        order_by = qp.pop("order_by", None)

        mapped = self._map_filter_names(qp, property_name_map, reverse_map)

        converted = {}
        for name, value in mapped.items():
            parts = name.split("__")
            raw = parts[0].lstrip("-")
            suffix = f"__{parts[-1]}" if len(parts) > 1 else ""
            kql_name = self._PROPERTY_TO_KQL.get(raw, raw)
            if parts[0].startswith("-"):
                converted[f"-{kql_name}{suffix}"] = value
            else:
                converted[f"{kql_name}{suffix}"] = value

        response, self.total_rows = self.client.search(
            search=search,
            filters=converted,
            page=page,
            searchable_properties=set(self._PROPERTY_TO_KQL.values()),
            reverse_map=reverse_map,
            order_by=order_by,
        )
        return response


class DRPGraphClient(GraphClient):
    """GraphClient that delegates sorting to the parent's search()."""
