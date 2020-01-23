from django.conf import settings

from rest_framework import serializers
from rest_framework.reverse import reverse

from donor_reporting_portal.libraries.sharepoint.serializers import (
    SharePointPropertyField,
    SharePointPropertyManyField,
    UpperSharePointPropertyField,
)


class SharePointItemSerializer(serializers.Serializer):

    id = UpperSharePointPropertyField()
    guid = UpperSharePointPropertyField()
    created = SharePointPropertyField()
    modified = SharePointPropertyField()
    report_generated_by = SharePointPropertyField()
    title = SharePointPropertyField()
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
    url = SharePointPropertyField()
    description = SharePointPropertyField()
    resource_url = serializers.ReadOnlyField()
    download_url = serializers.SerializerMethodField()

    def get_download_url(self, obj):
        filename = obj.properties.get('Title', '')
        if filename:
            k = filename.rfind(".")
            filename = filename[:k] + "__ext__" + filename[k + 1:]
        relative_url = reverse('api:sharepoint-files-download', kwargs={
            'site_name': self.context['site_name'],
            'folder_name': self.context['folder_name'],
            'filename': filename
        })
        return f'{settings.HOST}{relative_url}'


class SharePointFileSerializer(serializers.Serializer):
    name = SharePointPropertyField()
    type_name = serializers.ReadOnlyField()
    url = serializers.ReadOnlyField()
    linking_uri = SharePointPropertyField()
    server_relative_url = SharePointPropertyField()
    unique_id = SharePointPropertyField()
    title = SharePointPropertyField()
    time_created = SharePointPropertyField()
    time_last_modified = SharePointPropertyField()
    download_url = serializers.SerializerMethodField()

    def get_download_url(self, obj):
        relative_url = reverse('api:sharepoint-files-download', kwargs={
            'site_name': self.context['site_name'],
            'folder_name': self.context['folder_name'],
            'filename': obj.properties['Name'].split('.')[0]})
        return f'{settings.HOST}{relative_url}'
