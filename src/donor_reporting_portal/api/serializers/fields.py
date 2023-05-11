from rest_framework import serializers
from sharepoint_rest_api.utils import to_camel


class SearchSharePointField(serializers.ReadOnlyField):
    def get_attribute(self, instance):
        field_name = self.prefix + to_camel(self.source)
        return instance.get(field_name, "N/A")


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
