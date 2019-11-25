from django.urls import include, path

from rest_framework import routers

from donor_reporting_portal.api.views.static import MetadataStaticAPIView

from .views.metadata import DonorViewSet, ExternalGrantViewSet, GrantViewSet, ThemeViewSet
from .views.sharepoint import (
    FileSharePointViewSet,
    ItemSharePointViewSet,
    SharePointLibraryViewSet,
    SharePointSiteViewSet,
    ItemSharePointCamlViewSet)
from .views.userrole import BusinessAreaViewSet, GroupViewSet, UserRoleViewSet, UserViewSet

app_name = 'donors'

router = routers.DefaultRouter()
router.register(r'roles/groups', GroupViewSet)
router.register(r'roles/users', UserViewSet)
router.register(r'roles/user-role', UserRoleViewSet)
router.register(r'roles/business-area', BusinessAreaViewSet)
router.register(r'metadata/themes', ThemeViewSet)
router.register(r'metadata/donors', DonorViewSet)
router.register(r'metadata/external_grant/(?P<donor_id>\d+)', ExternalGrantViewSet, basename='external_grant')
router.register(r'metadata/grants/(?P<donor_id>\d+)', GrantViewSet, basename='grant')
router.register(r'sharepoint/sites', SharePointSiteViewSet, basename='sharepoint-site')
router.register(r'sharepoint/libraries', SharePointLibraryViewSet, basename='sharepoint-library')
router.register(r'sharepoint/(?P<site_name>[\w\-]+)/(?P<folder_name>[\w|\W]+)/files', FileSharePointViewSet,
                basename='sharepoint-files')
router.register(r'sharepoint/(?P<site_name>[\w\-]+)/(?P<folder_name>[\w|\W]+)', ItemSharePointViewSet,
                basename='sharepoint')
router.register(r'sharepoint-caml/(?P<site_name>[\w\-]+)/(?P<folder_name>[\w|\W]+)', ItemSharePointCamlViewSet,
                basename='sharepoint-caml')

urlpatterns = [
    path('metadata/static/', view=MetadataStaticAPIView.as_view(http_method_names=['get']),
         name='dropdown-static-list'),
    path(r'', include(router.urls)),
]
