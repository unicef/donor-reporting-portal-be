from rest_framework import viewsets
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
    serializer_class = DRPSharePointSearchSerializer
    select_fields = (
        'Title',
        'Path',
        'FileExtension',
        'DRPDonor',
        'DRPGrantNumber',
        'DRPDonorDocument',
        'ECMDocumentType',
        'Author',
        'DRPReportEndDate',
        'DRPTheme',
        'DRPDonorReportCategory'
    )


class DRPSharePointSettingsSearchViewSet(DRPSharepointSearchMixin, SharePointSettingsSearchViewSet):
    pass


class DRPSharePointUrlSearchViewSet(DRPSharepointSearchMixin, SharePointUrlSearchViewSet):
    pass
