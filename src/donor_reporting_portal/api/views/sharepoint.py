from urllib.parse import urlencode

from rest_framework import viewsets
from sharepoint_rest_api.utils import to_camel
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


class DonorReportingViewSet:
    permission_classes = ((DonorPermission | PublicLibraryPermission),)


class DRPSharePointSettingsRestViewSet(DonorReportingViewSet, SharePointSettingsRestViewSet):
    serializer_class = DRPSharePointSettingsSerializer


class DRPSharePointSettingsCamlViewSet(DonorReportingViewSet, SharePointSettingsCamlViewSet):
    serializer_class = DRPSharePointSettingsSerializer


class DRPSharePointUrlRestViewSet(DonorReportingViewSet, SharePointUrlRestViewSet):
    serializer_class = DRPSharePointUrlSerializer


class DRPSharePointUrlCamlViewSet(DonorReportingViewSet, SharePointUrlCamlViewSet):
    serializer_class = DRPSharePointUrlSerializer


class DRPSharePointUrlFileViewSet(DonorReportingViewSet, SharePointUrlFileViewSet):
    pass


class DRPSharePointSettingsFileViewSet(DonorReportingViewSet, SharePointSettingsFileViewSet):
    pass


class DRPSharepointSearchMixin:
    prefix = 'DRP'
    serializer_class = DRPSharePointSearchSerializer

    def get_selected(self, selected):
        def to_drp(source):
            return self.prefix + to_camel(source)
        selected = super().get_selected(selected)
        return [to_drp(x) for x in selected] + ["Title", "Author", "Path"]

    def get_filters(self, kwargs):
        # we can enforce filters here
        new_kwargs = {
            'IsDocument': '1',
            'DRPReportStatus': 'Certified by Comptroller,Pending Approval by Comptroller'
        }
        for key, value in kwargs.items():
            new_key = self.prefix + to_camel(key)
            if key in self.serializer_class._declared_fields.keys():
                new_kwargs[new_key] = value
            else:
                new_kwargs[key] = value

        return new_kwargs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        next_offset = int(self.request.query_params.get('page', 1)) + 1
        prev_offset = int(self.request.query_params.get('page', 1)) - 1
        next_dict = request.query_params.copy()
        next_dict['page'] = str(next_offset)
        prev_dict = request.query_params.copy()
        prev_dict['page'] = str(prev_offset)
        response.data = {
            "items": response.data,
            "next:": request.build_absolute_uri('?') + '?' + urlencode(next_dict),
            "previous": request.build_absolute_uri('?') + '?' + urlencode(prev_dict)
        }
        return response


class DRPSharePointSettingsSearchViewSet(DonorReportingViewSet, DRPSharepointSearchMixin,
                                         SharePointSettingsSearchViewSet):
    pass


class DRPSharePointUrlSearchViewSet(DonorReportingViewSet, DRPSharepointSearchMixin, SharePointUrlSearchViewSet):
    pass
