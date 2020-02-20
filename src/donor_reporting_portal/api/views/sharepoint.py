from unicef_sharepoint.views import ItemSharePointCamlViewSet, ItemSharePointViewSet

from donor_reporting_portal.api.permissions import DonorPermission, PublicLibraryPermission
from donor_reporting_portal.api.serializers.sharepoint import DRPSharePointItemSerializer


class DonorReportingViewSet:
    permission_classes = ((DonorPermission | PublicLibraryPermission),)


class DRPItemSharePointViewSet(DonorReportingViewSet, ItemSharePointViewSet):
    serializer_class = DRPSharePointItemSerializer


class DRPItemSharePointCamlViewSet(DonorReportingViewSet, ItemSharePointCamlViewSet):
    serializer_class = DRPSharePointItemSerializer
