from datetime import datetime

from django.conf import settings

from dateutil.parser import parse
from rest_framework import serializers
from rest_framework.reverse import reverse
from sharepoint_rest_api.serializers.fields import (
    CapitalizeSearchSharePointField,
    SharePointPropertyField,
    SharePointPropertyManyField,
)
from sharepoint_rest_api.serializers.sharepoint import SharePointSettingsSerializer, SharePointUrlSerializer

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

    def get_is_new(self, obj):
        modified = obj.get("DRPModified")

        if modified:
            try:
                day_difference = (datetime.now() - parse(modified, ignoretz=True)).days
                return day_difference <= 3
            except (TypeError, ValueError):
                return False

    def get_download_url(self, obj):
        try:
            path = obj.get("Path")
            directories = path.split("/")
            relative_url = reverse(
                "sharepoint_rest_api:sharepoint-settings-files-download",
                kwargs={"folder": directories[-2], "filename": directories[-1]},
            )
            base_url = f"{settings.HOST}{relative_url}"
            donor_code = obj.get("DRPDonorCode")
            if donor_code:
                donor_code = donor_code.replace(";", ",")
                base_url = f"{base_url}?donor_code={donor_code}"
            return base_url
        except BaseException:
            return None


class DRPSharePointSearchSerializer(DRPSharePointBaseSerializer):
    report_generated_by = DRPSearchSharePointField()
    donor = DRPSearchSharePointField()
    donor_code = DRPSearchSharePointField()
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
        "DRPDonorDocument" "DRPReportMethod",
        "DRPReportGroup",
        "DRPReportStatus" "DRPRetracted",
        "DRPFrameworkAgreement",
        "DRPAwardType",
    ]


class GaviSharePointSearchSerializer(DRPSharePointBaseSerializer):
    donor_code = DRPSearchSharePointField()
    number = CTNSearchSharePointField()
    m_o_u_number = CTNSearchSharePointField()
    m_o_u_r_eference = CTNSearchSharePointField()
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
