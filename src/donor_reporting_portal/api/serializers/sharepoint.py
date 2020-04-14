from datetime import datetime

from rest_framework import serializers
from unicef_sharepoint.serializers import (
    SharePointItemSerializer,
    SharePointPropertyField,
    SharePointPropertyManyField,
    SimpleSharePointItemSerializer,
)

from donor_reporting_portal.apps.sharepoint.models import SharePointGroup


class SharePointGroupSerializer(serializers.ModelSerializer):
    libraries = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)

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


class DRPSharePointItemSerializer(SharePointItemSerializer, DRPSerializerMixin):
    pass


class DRPSimpleSharePointItemSerializer(SimpleSharePointItemSerializer, DRPSerializerMixin):
    pass
