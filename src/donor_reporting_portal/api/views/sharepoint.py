from rest_framework import viewsets
from unicef_sharepoint.views import FileSharePointViewSet, ItemSharePointCamlViewSet, ItemSharePointViewSet

from donor_reporting_portal.api.permissions import DonorPermission, PublicLibraryPermission
from donor_reporting_portal.api.serializers.sharepoint import DRPSharePointItemSerializer, SharePointGroupSerializer
from donor_reporting_portal.apps.sharepoint.models import SharePointGroup


class SharePointGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SharePointGroup.objects.all()
    serializer_class = SharePointGroupSerializer


class DonorReportingViewSet:
    permission_classes = ((DonorPermission | PublicLibraryPermission),)


class DRPItemSharePointViewSet(DonorReportingViewSet, ItemSharePointViewSet):
    serializer_class = DRPSharePointItemSerializer


class DRPItemSharePointCamlViewSet(DonorReportingViewSet, ItemSharePointCamlViewSet):
    serializer_class = DRPSharePointItemSerializer


class DRPFileSharePointViewSet(DonorReportingViewSet, FileSharePointViewSet):
    pass
