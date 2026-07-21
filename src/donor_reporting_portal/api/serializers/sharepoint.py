from datetime import datetime
from urllib.parse import unquote, urlparse

from django.conf import settings
from django.urls import reverse

from dateutil.parser import parse
from rest_framework import serializers
from sharepoint_rest_api import config as sp_config
from sharepoint_rest_api.serializers.fields import (
    CapitalizeSearchSharePointField,
    SharePointPropertyField,
    SharePointPropertyManyField,
)
from sharepoint_rest_api.serializers.sharepoint import SharePointSettingsSerializer, SharePointUrlSerializer
from sharepoint_rest_api.utils import to_camel

from donor_reporting_portal.api.serializers.fields import (
    CTNSearchMultiSharePointField,
    CTNSearchSharePointField,
    DRPSearchMultiSharePointField,
    DRPSearchSharePointField,
)
from donor_reporting_portal.apps.sharepoint.models import SharePointGroup

GRAPH_FILES_DOWNLOAD = "api:sharepoint-graph-files-download"


def _normalize_filename(raw):
    """Ensure *raw* has a double extension (e.g. ``file.pdf``).

    SharePoint stores files with a single extension like ``file.pdf``.
    The download endpoint expects ``file..pdf`` so that it can split on
    the last dot and reconstruct the original name.  If *raw* already
    has a dot, the extension is duplicated; otherwise ``.pdf`` is appended.
    """
    if not raw:
        return raw
    k = raw.rfind(".")
    if k > 0:
        return raw[:k] + "." + raw[k + 1 :]
    return f"{raw}.pdf"


def _graph_download_url(folder, filename, params=None):
    """Build a full download URL pointing at the Graph API proxy."""
    relative_url = reverse(
        GRAPH_FILES_DOWNLOAD,
        kwargs={"folder": folder, "filename": _normalize_filename(filename)},
    )
    base = f"{settings.HOST}{relative_url}"
    if params:
        return f"{base}?{'&'.join(params)}"
    return base


class SharePointGroupSerializer(serializers.ModelSerializer):
    libs = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)

    class Meta:
        model = SharePointGroup
        fields = "__all__"


class DRPSerializerMixin(serializers.Serializer):
    report_generated_by = SharePointPropertyField()
    year = SharePointPropertyField()
    donor = SharePointPropertyField()
    donor_code = SharePointPropertyField()
    regenerated = SharePointPropertyField()
    grant_number = SharePointPropertyField()
    grant_issue_year = SharePointPropertyField()
    grant_expiry_date = SharePointPropertyField()
    external_reference = SharePointPropertyField()
    recipient_office = SharePointPropertyManyField()
    report_type = SharePointPropertyField()
    report_end_date = SharePointPropertyField()
    theme = SharePointPropertyField()
    donor_document = SharePointPropertyField()
    donor_report_category = SharePointPropertyField()
    report_method = SharePointPropertyField()
    report_group = SharePointPropertyField()
    report_period = SharePointPropertyField()
    report_status = SharePointPropertyField()
    retracted = SharePointPropertyField()
    description = SharePointPropertyField()
    framework_agreement = SharePointPropertyField()
    is_new = serializers.SerializerMethodField()

    def get_is_new(self, obj):
        modified = obj.get("Modified")
        if modified:
            modified = parse(modified[:19], ignoretz=True)
            day_difference = (datetime.now() - modified).days
            return day_difference <= 3
        return False

    def get_download_url(self, obj):
        folder = self.context.get("folder", "Documents")
        filename = obj.get("FileLeafRef") or obj.get("Title", "")
        params = []
        donor_code = obj.get("DonorCode", "")
        if donor_code:
            params.append(f"donor_code={donor_code.replace(';', ',')}")
        return _graph_download_url(folder, filename, params or None)


class DRPSharePointUrlSerializer(DRPSerializerMixin, SharePointUrlSerializer):
    pass


class DRPSharePointSettingsSerializer(DRPSerializerMixin, SharePointSettingsSerializer):
    pass


class DRPSharePointBaseSerializer(serializers.Serializer):
    title = CapitalizeSearchSharePointField()
    author = CapitalizeSearchSharePointField()
    path = CapitalizeSearchSharePointField()

    created = DRPSearchSharePointField()
    modified = DRPSearchSharePointField()

    is_new = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    export_headers = [
        "Title",
    ]

    @classmethod
    def get_property_name_map(cls):
        """Build dict mapping URL param names → search managed property names.

        Derived dynamically from each field's `get_search_property()` method.
        Fields without `get_search_property()` (e.g. CapitalizeSearchSharePointField)
        default to `to_camel(source)`.
        """
        instance = cls()
        mapping = {}
        for name, field in instance.fields.items():
            if hasattr(field, "get_search_property"):
                mapping[name] = field.get_search_property()
            else:
                mapping[name] = to_camel(name)
        return mapping

    @classmethod
    def get_property_name_reverse(cls):
        """Build dict mapping managed property names → serializer field names.

        e.g. {'DonorCode': 'DRPDonorCode', 'GrantNumber': 'DRPGrantNumber'}
        Ensures the serializer's `DRPSearchSharePointField` can find values
        by `DRP`+PascalCase name in the enriched item dict.
        """
        instance = cls()
        mapping = {}
        for name, field in instance.fields.items():
            if hasattr(field, "get_serializer_field_name"):
                managed_name = to_camel(name)
                serializer_name = field.get_serializer_field_name()
                if managed_name != serializer_name:
                    mapping[managed_name] = serializer_name
        return mapping

    def get_is_new(self, obj):
        modified = obj.get("DRPModified")

        if modified:
            try:
                day_difference = (datetime.now() - parse(modified, ignoretz=True)).days
                return day_difference <= 3
            except (TypeError, ValueError):
                pass
        return False

    def get_download_url(self, obj):
        try:
            path = obj.get("Path")
            if not path:
                return None
            relative_path = self._extract_site_relative_path(path)
            if not relative_path:
                return None
            parts = relative_path.rsplit("/", 1)
            if len(parts) != 2:
                return None
            folder, filename = parts
            params = []
            donor_code = obj.get("DRPDonorCode")
            if donor_code:
                params.append(f"donor_code={donor_code.replace(';', ',')}")
            site_id = obj.get("SiteId")
            if site_id:
                params.append(f"site_id={site_id}")
            drive_id = obj.get("DriveId")
            if drive_id:
                params.append(f"drive_id={drive_id}")
            doc_id = obj.get("DocId")
            if doc_id:
                params.append(f"item_id={doc_id}")
            if not site_id and not (drive_id and doc_id):
                return None
            return _graph_download_url(folder, filename, params)
        except (KeyError, IndexError):
            return None

    @staticmethod
    def _extract_site_relative_path(path):
        """Extract the site-relative path from a SharePoint webUrl.

        Converts e.g. 'https://tenant.sharepoint.com/sites/GLB-DRP/Shared%20Documents/file.pdf'
        to 'Shared Documents/file.pdf'.
        """
        parsed = urlparse(path)
        url_path = unquote(parsed.path) if parsed.scheme else unquote(path)
        url_path = url_path.lstrip("/")
        site_prefix = f"{sp_config.SHAREPOINT_SITE_TYPE}/{sp_config.SHAREPOINT_SITE}/"
        if url_path.startswith(site_prefix):
            return url_path[len(site_prefix) :]
        segments = url_path.split("/")
        if len(segments) >= 3 and segments[0] == sp_config.SHAREPOINT_SITE_TYPE:
            return "/".join(segments[2:])
        return "/".join(segments[1:]) if len(segments) > 1 else None


class DRPSharePointSearchSerializer(DRPSharePointBaseSerializer):
    report_generated_by = DRPSearchSharePointField()
    donor = DRPSearchSharePointField()
    donor_code = DRPSearchSharePointField(search_property="Donor")
    grant_number = DRPSearchSharePointField()
    grant_issue_year = DRPSearchSharePointField()
    grant_expiry_date = DRPSearchSharePointField()
    external_reference = DRPSearchSharePointField()
    recipient_office = DRPSearchMultiSharePointField()
    report_type = DRPSearchSharePointField()
    report_end_date = DRPSearchSharePointField()
    theme = DRPSearchSharePointField()
    donor_document = DRPSearchSharePointField()
    donor_report_category = DRPSearchSharePointField()
    report_method = DRPSearchSharePointField()
    report_group = DRPSearchSharePointField()
    report_status = DRPSearchSharePointField()
    retracted = DRPSearchSharePointField()
    framework_agreement = DRPSearchSharePointField()
    award_type = DRPSearchSharePointField()

    export_headers = [
        "DRPDonor",
        "DRPGrantNumber",
        "DRPIssueYear",
        "DRPExternalReference",
        "DRPRecipientOffice",
        "DRPReportType",
        "DRPTheme",
        "DRPDonorDocumentDRPReportMethod",
        "DRPReportGroup",
        "DRPReportStatusDRPRetracted",
        "DRPFrameworkAgreement",
        "DRPAwardType",
    ]


class GaviSharePointSearchSerializer(DRPSharePointBaseSerializer):
    donor_code = DRPSearchSharePointField(search_property="Donor")
    number = CTNSearchSharePointField()
    m_o_u_number = CTNSearchSharePointField()
    m_o_u_r_eference = CTNSearchSharePointField(search_property="MOUReference")
    sent_to_g_a_v_i_date = CTNSearchSharePointField()
    funds_due_date = CTNSearchSharePointField()
    g_a_v_i_w_b_s = CTNSearchMultiSharePointField()
    country_name = CTNSearchMultiSharePointField()
    vaccine_type = CTNSearchMultiSharePointField()
    purchase_order = CTNSearchMultiSharePointField()
    material_code = CTNSearchMultiSharePointField()
    approval_year = CTNSearchSharePointField()
    prepaid_status = CTNSearchSharePointField()
    allocation_round = CTNSearchSharePointField()
    vendor = CTNSearchSharePointField()
    urgent = CTNSearchSharePointField()

    export_headers = [
        "CTNNumber",
        "CTNMOUNumber",
        "CTNMOUREference",
        "CTNSentToGAVIDate",
        "CTNFundsDueDate",
        "CTNGAVIWBS",
        "CTNCountryName",
        "CTNVaccineType",
        "CTNPurchaseOrder",
        "CTNMaterialCode",
        "CTNApprovalYear",
        "CTNPrepaidStatus",
        "CTNAllocationRound",
        "CTNVendor",
        "CTNUrgent",
        "Title",
    ]


class GaviSoaSharePointSearchSerializer(DRPSharePointBaseSerializer):
    grant_number = DRPSearchSharePointField()
    donor_code = DRPSearchSharePointField(search_property="Donor")
    g_a_v_i_w_b_s = CTNSearchMultiSharePointField()
    sent_to_g_a_v_i_date = CTNSearchSharePointField()
    purchase_order = CTNSearchMultiSharePointField()
    u_n_i_c_e_f_w_b_s = CTNSearchSharePointField()
    s_o_a_issue_date = CTNSearchSharePointField()
    country_name = CTNSearchMultiSharePointField()
    m_o_u_number = CTNSearchSharePointField()
    approval_year = CTNSearchSharePointField()
    material_code = CTNSearchMultiSharePointField()
    vaccine_type = CTNSearchMultiSharePointField()

    export_headers = [
        "DRPGrantNumber",
        "CTNGAVIWBS",
        "CTNPurchaseOrder",
        "CTNUNICEFWBS",
        "CTNSOAIssueDate",
        "CTNCountryName",
        "CTNMOUNumber",
        "CTNApprovalYear",
        "CTNMaterialCode",
        "CTNVaccineType",
    ]
