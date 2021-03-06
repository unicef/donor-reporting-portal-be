from django.conf import settings

from rest_framework import viewsets
from sharepoint_rest_api.utils import to_camel
from sharepoint_rest_api.views.base import SharePointSearchViewSet
from sharepoint_rest_api.views.settings_based import (
    SharePointSettingsCamlViewSet,
    SharePointSettingsFileViewSet,
    SharePointSettingsRestViewSet,
    SharePointSettingsSearchViewSet,
)
from sharepoint_rest_api.views.url_based import (
    SharePointUrlCamlViewSet,
    SharePointUrlFileViewSet,
    SharePointUrlRestViewSet,
    SharePointUrlSearchViewSet,
)

from donor_reporting_portal.api.permissions import DonorPermission, PublicLibraryPermission
from donor_reporting_portal.api.serializers.fields import DRPSearchSharePointField
from donor_reporting_portal.api.serializers.sharepoint import (
    DRPSharePointSearchSerializer,
    DRPSharePointSettingsSerializer,
    DRPSharePointUrlSerializer,
    SharePointGroupSerializer,
)
from donor_reporting_portal.apps.sharepoint.models import SharePointGroup


class SharePointGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SharePointGroup.objects.all()
    serializer_class = SharePointGroupSerializer


class DRPViewSet:
    permission_classes = ((DonorPermission | PublicLibraryPermission),)


class DRPSharePointSettingsRestViewSet(DRPViewSet, SharePointSettingsRestViewSet):
    serializer_class = DRPSharePointSettingsSerializer


class DRPSharePointSettingsCamlViewSet(DRPViewSet, SharePointSettingsCamlViewSet):
    serializer_class = DRPSharePointSettingsSerializer


class DRPSharePointUrlRestViewSet(DRPViewSet, SharePointUrlRestViewSet):
    serializer_class = DRPSharePointUrlSerializer


class DRPSharePointUrlCamlViewSet(DRPViewSet, SharePointUrlCamlViewSet):
    serializer_class = DRPSharePointUrlSerializer


class DRPSharePointUrlFileViewSet(SharePointUrlFileViewSet):
    permission_classes = (DonorPermission,)


class DRPSharePointSettingsFileViewSet(SharePointSettingsFileViewSet):
    permission_classes = (DonorPermission, )


class DRPSharepointSearchViewSet(SharePointSearchViewSet):
    prefix = 'DRP'
    serializer_class = DRPSharePointSearchSerializer

    def is_public(self):
        """check if the source id is public or restricted to UNICEF users"""
        source_id = self.request.query_params.get('source_id', None)
        public = source_id in [settings.DRP_SOURCE_IDS['thematic_internal'],
                               settings.DRP_SOURCE_IDS['thematic_external']]
        if public:
            return True
        unicef_user = self.request.user.username.endswith('@unicef.org')
        return unicef_user and source_id in [settings.DRP_SOURCE_IDS['internal'],
                                             settings.DRP_SOURCE_IDS['pool_internal']]

    def get_selected(self, selected):
        def to_drp(source):
            return self.prefix + to_camel(source)
        selected = super().get_selected(selected)
        return [to_drp(x) for x in selected] + ["Title", "Author", "Path"]

    def get_filters(self, kwargs):
        # we can enforce filters here
        new_kwargs = {
            # 'IsDocument': '1',
        }
        drp_fields = [key for key, value in self.serializer_class._declared_fields.items()
                      if isinstance(value, DRPSearchSharePointField)]

        for key, value in kwargs.items():
            key_splits = key.split('__')
            filter_name = key_splits[0]
            filter_type = key_splits[-1] if len(key_splits) > 1 else None
            if filter_name in drp_fields:
                new_key = self.prefix + to_camel(filter_name)
                if filter_type:
                    new_key = f'{new_key}__{filter_type}'
                new_kwargs[new_key] = value
            else:
                new_kwargs[key] = value

        return new_kwargs


class DRPSharePointSettingsSearchViewSet(DRPViewSet, DRPSharepointSearchViewSet, SharePointSettingsSearchViewSet):
    """DRP Search Viewset for settings based"""


class DRPSharePointUrlSearchViewSet(DRPViewSet, DRPSharepointSearchViewSet, SharePointUrlSearchViewSet):
    """DRP Search Viewset for url based"""
