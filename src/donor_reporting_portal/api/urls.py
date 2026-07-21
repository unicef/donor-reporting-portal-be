from django.urls import include, path

from rest_framework import routers

from donor_reporting_portal.api.views.config import ConfigAPIView
from donor_reporting_portal.api.views.static import MetadataStaticAPIView

from .views.metadata import (
    DonorViewSet,
    DRPMetadataViewSet,
    ExternalGrantViewSet,
    GrantViewSet,
    SecondaryDonorViewSet,
    ThemeViewSet,
)
from .views.sharepoint import (
    DRPGraphBasedSearchViewSet,
    DRPGraphFileDownloadViewSet,
    SharePointGroupViewSet,
)
from .views.userrole import BusinessAreaViewSet, GroupViewSet, UserRoleViewSet, UserViewSet

app_name = "api"

router = routers.DefaultRouter()
router.register(r"roles/groups", GroupViewSet)
router.register(r"roles/users", UserViewSet)
router.register(r"roles/user-role", UserRoleViewSet)
router.register(r"roles/business-area", BusinessAreaViewSet)
router.register(r"metadata/themes", ThemeViewSet)
router.register(r"metadata/donors", DonorViewSet)
router.register(
    r"metadata/external_grant/(?P<donor_id>\d+)",
    ExternalGrantViewSet,
    basename="external_grant",
)
router.register(r"metadata/grants/(?P<donor_id>\d+)", GrantViewSet, basename="grant")
router.register(r"metadata/drp-static", DRPMetadataViewSet)
router.register(r"metadata/secondary-donors", SecondaryDonorViewSet, basename="secondary-donor")
router.register(r"sharepoint/groups", SharePointGroupViewSet, basename="sharepoint-group")

router.register(
    r"graph/(?P<folder>[\w\W]+)/files",
    DRPGraphFileDownloadViewSet,
    basename="sharepoint-graph-files",
)
router.register(
    r"sharepoint/search",
    DRPGraphBasedSearchViewSet,
    basename="sharepoint-search",
)
router.register(
    r"graph/search",
    DRPGraphBasedSearchViewSet,
    basename="graph-search",
)

urlpatterns = [
    path(
        "metadata/static/",
        view=MetadataStaticAPIView.as_view(http_method_names=["get"]),
        name="metadata-static-list",
    ),
    path(
        "config/",
        view=ConfigAPIView.as_view(http_method_names=["get"]),
        name="config-list",
    ),
    path(r"", include(router.urls)),
]
