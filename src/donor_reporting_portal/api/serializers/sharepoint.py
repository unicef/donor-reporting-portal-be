from datetime import datetime

from django.conf import settings

from rest_framework import serializers
from rest_framework.reverse import reverse
from sharepoint_rest_api.serializers.fields import (
    CapitalizeSearchSharePointField,
    SharePointPropertyField,
    SharePointPropertyManyField,
)
from sharepoint_rest_api.serializers.sharepoint import SharePointSettingsSerializer, SharePointUrlSerializer

from donor_reporting_portal.api.serializers.fields import DRPSearchMultiSharePointField, DRPSearchSharePointField
from donor_reporting_portal.apps.sharepoint.models import SharePointGroup


class SharePointGroupSerializer(serializers.ModelSerializer):
    libs = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)

    class Meta:
        model = SharePointGroup
        fields = '__all__'


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
        modified = datetime.strptime(obj.properties['Modified'][:19], '%Y-%m-%dT%H:%M:%S')
        day_difference = (datetime.now() - modified).days
        return day_difference <= 3

    def get_download_url(self, obj):
        base_url = super().get_download_url(obj)
        return '{}?donor_code={}'.format(base_url, obj.properties['DonorCode'])


class DRPSharePointUrlSerializer(DRPSerializerMixin, SharePointUrlSerializer):
    pass


class DRPSharePointSettingsSerializer(DRPSerializerMixin, SharePointSettingsSerializer):
    pass


class DRPSharePointSearchSerializer(serializers.Serializer):
    title = CapitalizeSearchSharePointField()
    author = CapitalizeSearchSharePointField()
    path = CapitalizeSearchSharePointField()

    created = DRPSearchSharePointField()
    modified = DRPSearchSharePointField()
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

    is_new = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    def get_is_new(self, obj):
        field_name = 'DRPModified'
        items = [item['Value'] for item in obj if item['Key'] == field_name]
        modified = items[0] if items else None
        if modified:
            day_difference = (datetime.now() - datetime.strptime(modified, '%m/%d/%Y %H:%M:%S %p')).days
            return day_difference <= 3

    def get_download_url(self, obj):
        try:
            path = [item['Value'] for item in obj if item['Key'] == 'Path'][0]
            directories = path.split('/')
            relative_url = reverse('sharepoint_rest_api:sharepoint-settings-files-download', kwargs={
                'folder': directories[-2],
                'filename': directories[-1]
            })
            return f'{settings.HOST}{relative_url}'
        except BaseException:
            return None
