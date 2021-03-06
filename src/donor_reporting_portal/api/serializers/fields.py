from rest_framework import serializers
from sharepoint_rest_api.utils import to_camel

from donor_reporting_portal.api.serializers.utils import getvalue


class DRPSearchSharePointField(serializers.ReadOnlyField):
    prefix = 'DRP'

    def get_attribute(self, instance):
        field_name = self.prefix + to_camel(self.source)
        return getvalue(instance, field_name)


class DRPSearchMultiSharePointField(DRPSearchSharePointField):
    def get_attribute(self, instance):
        attrs = super().get_attribute(instance)
        return attrs.split(';') if attrs else []
