from rest_framework import serializers
from sharepoint_rest_api.utils import to_camel

from donor_reporting_portal.api.serializers.utils import getvalue


class SearchSharePointField(serializers.ReadOnlyField):
    def get_attribute(self, instance):
        field_name = self.prefix + to_camel(self.source)
        return getvalue(instance, field_name)


class SearchMultiSharePointField(serializers.ReadOnlyField):
    def get_attribute(self, instance):
        attrs = super().get_attribute(instance)
        return list(filter(None, attrs.split(";"))) if attrs else []


class DRPSearchSharePointField(SearchSharePointField):
    prefix = "DRP"


class CTNSearchSharePointField(SearchSharePointField):
    prefix = "CTN"


class DRPSearchMultiSharePointField(SearchMultiSharePointField, DRPSearchSharePointField):
    pass


class CTNSearchMultiSharePointField(SearchMultiSharePointField, CTNSearchSharePointField):
    pass
