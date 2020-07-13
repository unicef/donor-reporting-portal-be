from rest_framework import viewsets
from unicef_sharepoint.views import (
    FileSharePointViewSet,
    ItemSharePointCamlViewSet,
    ItemSharePointViewSet,
    SharePointCamlViewSet,
    SharePointFileViewSet,
    SharePointRestViewSet,
)

from donor_reporting_portal.api.permissions import DonorPermission, PublicLibraryPermission
from donor_reporting_portal.api.serializers.sharepoint import (
    DRPSharePointItemSerializer,
    DRPSimpleSharePointItemSerializer,
    SharePointGroupSerializer,
)
from donor_reporting_portal.apps.sharepoint.models import SharePointGroup


class SharePointGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SharePointGroup.objects.all()
    serializer_class = SharePointGroupSerializer


class DonorReportingViewSet:
    permission_classes = ((DonorPermission | PublicLibraryPermission),)


class DRPSharePointRestViewSet(DonorReportingViewSet, SharePointRestViewSet):
    serializer_class = DRPSimpleSharePointItemSerializer


class DRPSharePointCamlViewSet(DonorReportingViewSet, SharePointCamlViewSet):
    serializer_class = DRPSimpleSharePointItemSerializer


class DRPItemSharePointViewSet(DonorReportingViewSet, ItemSharePointViewSet):
    serializer_class = DRPSharePointItemSerializer


class DRPItemSharePointCamlViewSet(DonorReportingViewSet, ItemSharePointCamlViewSet):
    serializer_class = DRPSharePointItemSerializer


class DRPFileSharePointViewSet(DonorReportingViewSet, FileSharePointViewSet):
    pass


class DRPSharePointFileViewSet(DonorReportingViewSet, SharePointFileViewSet):
    pass
