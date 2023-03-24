from rest_framework import serializers

from donor_reporting_portal.apps.report_metadata.models import (
    Donor,
    DRPMetadata,
    ExternalGrant,
    Grant,
    SecondaryDonor,
    Theme,
)


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = "__all__"


class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = "__all__"


class DonorSecondaryDonorSerializer(DonorSerializer):
    secondary_donors = serializers.SerializerMethodField()

    def get_secondary_donors(self, obj):
        qs = SecondaryDonor.objects.filter(grants__donor=obj)
        return SecondaryDonorSerializer(qs, many=True).data


class ExternalGrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalGrant
        fields = "__all__"


class GrantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grant
        fields = "__all__"


class SecondaryDonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondaryDonor
        fields = "__all__"


class DRPMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DRPMetadata
        fields = ("category", "code", "description", "audience")
