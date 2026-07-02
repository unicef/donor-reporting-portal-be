from rest_framework import serializers
from rest_framework.fields import SkipField
from sharepoint_rest_api.utils import to_camel


class SearchSharePointField(serializers.ReadOnlyField):
    prefix = ""

    def __init__(self, search_property=None, **kwargs):
        self.search_property = search_property
        super().__init__(**kwargs)

    def get_attribute(self, instance):
        field_name = self.prefix + to_camel(self.source)
        return instance.get(field_name, "N/A")

    def get_search_property(self):
        """Return the managed property name for KQL search filtering.

        By default, uses `to_camel(source)`. Override by passing
        `search_property` to the field constructor (e.g. for fields where
        the managed property name differs from the usual convention).
        """
        if self.search_property:
            return self.search_property
        if self.source is None:
            return None
        return to_camel(self.source)

    def get_serializer_field_name(self):
        """Return the key this field looks for in the response dict."""
        return self.prefix + to_camel(self.source)


class SearchMultiSharePointField(serializers.ReadOnlyField):
    def get_attribute(self, instance):
        try:
            attrs = super().get_attribute(instance)
        except SkipField:
            return []
        return list(filter(None, attrs.split(";"))) if attrs else []


class DRPSearchSharePointField(SearchSharePointField):
    prefix = "DRP"


class CTNSearchSharePointField(SearchSharePointField):
    prefix = "CTN"


class DRPSearchMultiSharePointField(SearchMultiSharePointField, DRPSearchSharePointField):
    pass


class CTNSearchMultiSharePointField(SearchMultiSharePointField, CTNSearchSharePointField):
    pass
