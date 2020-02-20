from rest_framework import serializers

from donor_reporting_portal.apps.report_metadata.models import Donor, ExternalGrant, Grant, Theme


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
