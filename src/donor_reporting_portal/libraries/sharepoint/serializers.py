from office365.sharepoint.helpers.utils import to_camel
from rest_framework import serializers


class SharePointPropertyField(serializers.ReadOnlyField):
    """tries to get attribute from the object or properties"""

    def get_attribute(self, instance):
        camel_case = to_camel(self.source)
        if getattr(instance, 'properties') and camel_case in instance.properties:
            return instance.properties[camel_case]
        return super().get_attribute(instance)


class SharePointPropertyManyField(serializers.ReadOnlyField):
    """tries to get attribute from the object or properties"""

    def get_attribute(self, instance):
        camel_case = to_camel(self.source)
        if getattr(instance, 'properties') and camel_case in instance.properties:
            values = instance.properties[camel_case]
            if values:
                values = values.replace(', ', ',').split(',')
            return values
        return super().get_attribute(instance)


class UpperSharePointPropertyField(serializers.ReadOnlyField):

    def get_attribute(self, instance):
        upper_case = self.source.upper()
        if getattr(instance, 'properties') and upper_case in instance.properties:
            return instance.properties[upper_case]
        return super().get_attribute(instance)
