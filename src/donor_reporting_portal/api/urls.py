from django.urls import include, path

from rest_framework import routers

from donor_reporting_portal.api.views.static import MetadataStaticAPIView

from .views.metadata import DonorViewSet, ExternalGrantViewSet, GrantViewSet, SecondaryDonorViewSet, ThemeViewSet
from .views.sharepoint import DRPItemSharePointCamlViewSet, DRPItemSharePointViewSet, SharePointGroupViewSet
from .views.userrole import BusinessAreaViewSet, GroupViewSet, UserRoleViewSet, UserViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'roles/groups', GroupViewSet)
router.register(r'roles/users', UserViewSet)
router.register(r'roles/user-role', UserRoleViewSet)
router.register(r'roles/business-area', BusinessAreaViewSet)
router.register(r'metadata/themes', ThemeViewSet)
router.register(r'metadata/donors', DonorViewSet)
router.register(r'metadata/external_grant/(?P<donor_id>\d+)', ExternalGrantViewSet, basename='external_grant')
router.register(r'metadata/grants/(?P<donor_id>\d+)', GrantViewSet, basename='grant')
router.register(r'metadata/secondary-donors', SecondaryDonorViewSet, basename='secondary-donor')
router.register(r'sharepoint/groups', SharePointGroupViewSet, basename='sharepoint-group')
router.register(r'sharepoint/(?P<tenant>[\w\-]+)/(?P<site>[\w\-]+)/(?P<folder>[\w|\W]+)/rest',
                DRPItemSharePointViewSet, basename='sharepoint')
router.register(r'sharepoint/(?P<tenant>[\w\-]+)/(?P<site>[\w\-]+)/(?P<folder>[\w|\W]+)/caml',
                DRPItemSharePointCamlViewSet, basename='sharepoint-caml')

urlpatterns = [
    path('metadata/static/', view=MetadataStaticAPIView.as_view(http_method_names=['get']),
         name='dropdown-static-list'),
    path(r'', include(router.urls)),
]
