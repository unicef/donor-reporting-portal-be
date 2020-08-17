from datetime import datetime

from django.conf import settings

from rest_framework import serializers
from rest_framework.reverse import reverse
from sharepoint_rest_api.serializers.fields import (
    RawSearchSharePointField,
    SearchSharePointField,
    SharePointPropertyField,
    SharePointPropertyManyField,
)
from sharepoint_rest_api.serializers.sharepoint import SharePointSettingsSerializer, SharePointUrlSerializer

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
        return True if day_difference <= 3 else False

    def get_download_url(self, obj):
        base_url = super().get_download_url(obj)
        return '{}?donor_code={}'.format(base_url, obj.properties['DonorCode'])


class DRPSharePointUrlSerializer(DRPSerializerMixin, SharePointUrlSerializer):
    pass


class DRPSharePointSettingsSerializer(DRPSerializerMixin, SharePointSettingsSerializer):
    pass


class DRPSharePointSearchSerializer(serializers.Serializer):
    title = SearchSharePointField()
    author = SearchSharePointField()
    path = SearchSharePointField()
    last_modified_time = SearchSharePointField()

    DRPDonor = RawSearchSharePointField()
    DRPGrantNumber = RawSearchSharePointField()
    DRPDonorDocument = RawSearchSharePointField()

    DRPReportEndDate = RawSearchSharePointField()
    DRPTheme = RawSearchSharePointField()
    DRPDonorReportCategory = RawSearchSharePointField()

    download_url = serializers.SerializerMethodField()

    def get_download_url(self, obj):
        filename = [item['Value'] for item in obj if item['Key'] == 'Title'][0]
        folder = self.context['folder']  # TODO
        relative_url = reverse('sharepoint_rest_api:sharepoint-settings-files-download', kwargs={
            'folder': folder,
            'filename': filename
        })
        return f'{settings.HOST}{relative_url}'
