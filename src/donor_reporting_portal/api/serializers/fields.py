from rest_framework import serializers
from sharepoint_rest_api.utils import to_camel


class DRPSearchSharePointField(serializers.ReadOnlyField):
    prefix = 'DRP'

    def get_attribute(self, instance):
        field_name = self.prefix + to_camel(self.source)
        items = [item['Value'] for item in instance if item['Key'] == field_name]
        return items[0] if items else 'N/A'


class DRPSearchMultiSharePointField(DRPSearchSharePointField):
    def get_attribute(self, instance):
        attrs = super().get_attribute(instance)
        return attrs.split(';') if attrs else []
