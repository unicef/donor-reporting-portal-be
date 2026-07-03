from datetime import datetime


from dateutil.parser import parse
from rest_framework import serializers
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
        base_url = super().get_download_url(obj)
        donor_code = obj["DonorCode"].replace(";", ",")
        return f"{base_url}?donor_code={donor_code}"


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
            donor_code = obj.get("DRPDonorCode")
            if donor_code:
                donor_code = donor_code.replace(";", ",")
                return f"{path}?donor_code={donor_code}"
            return path
        except (KeyError, IndexError):
            return None


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
