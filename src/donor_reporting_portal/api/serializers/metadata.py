from django.conf import settings
from django.urls import reverse

from rest_framework import serializers

from donor_reporting_portal.apps.report_metadata.models import Donor, ExternalGrant, Grant, Theme
from donor_reporting_portal.apps.sharepoint.models import SharePointLibrary, SharePointSite


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = '__all__'


class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = '__all__'


class ExternalGrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalGrant
        fields = '__all__'


class GrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grant
        fields = '__all__'


class SharePointSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharePointSite
        fields = '__all__'


class SharePointLibrarySerializer(serializers.ModelSerializer):
    site_name = serializers.ReadOnlyField(source='site.name')
    api_url = serializers.SerializerMethodField()

    def get_api_url(self, obj):
        reverse_url = reverse('api:sharepoint-list',
                              kwargs={'tenant': obj.site.tenant.name, 'site': obj.site.name, 'folder': obj.name})
        return settings.HOST + reverse_url

    class Meta:
        model = SharePointLibrary
        fields = ('name', 'site_name', 'active', 'library_url', 'api_url')
