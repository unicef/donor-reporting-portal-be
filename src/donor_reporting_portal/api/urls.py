from django.urls import include, path

from rest_framework import routers

from donor_reporting_portal.api.views.config import ConfigAPIView
from donor_reporting_portal.api.views.static import MetadataStaticAPIView

from .views.metadata import DonorViewSet, ExternalGrantViewSet, GrantViewSet, SecondaryDonorViewSet, ThemeViewSet
from .views.sharepoint import (
    DRPSharePointSettingsCamlViewSet,
    DRPSharePointSettingsFileViewSet,
    DRPSharePointSettingsRestViewSet,
    DRPSharePointSettingsSearchViewSet,
    DRPSharePointUrlCamlViewSet,
    DRPSharePointUrlFileViewSet,
    DRPSharePointUrlRestViewSet,
    DRPSharePointUrlSearchViewSet,
    SharePointGroupViewSet,
)
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

router.register(r'sharepoint/(?P<tenant>[\w\-]+)/(?P<site>[\w\-]+)/(?P<folder>[\w\W]+)/files',
                DRPSharePointUrlFileViewSet, basename='sharepoint-url-files')
router.register(r'sharepoint/(?P<tenant>[\w\-]+)/(?P<site>[\w\-]+)/(?P<folder>[\w|\W]+)/rest',
                DRPSharePointUrlRestViewSet, basename='sharepoint-url')
router.register(r'sharepoint/(?P<tenant>[\w\-]+)/(?P<site>[\w\-]+)/(?P<folder>[\w|\W]+)/caml',
                DRPSharePointUrlCamlViewSet, basename='sharepoint-url-caml')
router.register(r'sharepoint/(?P<tenant>[\w\-]+)/(?P<site>[\w\-]+)/search',
                DRPSharePointUrlSearchViewSet, basename='sharepoint-url-search')

router.register(r'sharepoint/(?P<folder>[\w\W]+)/rest',
                DRPSharePointSettingsRestViewSet, basename='sharepoint-settings-rest')
router.register(r'sharepoint/(?P<folder>[\w\W]+)/caml',
                DRPSharePointSettingsCamlViewSet, basename='sharepoint-settings-caml')
router.register(r'sharepoint/(?P<folder>[\w\W]+)/files',
                DRPSharePointSettingsFileViewSet, basename='sharepoint-settings-files')
router.register(r'sharepoint/search',
                DRPSharePointSettingsSearchViewSet, basename='sharepoint-settings-search')

urlpatterns = [
    path('metadata/static/', view=MetadataStaticAPIView.as_view(http_method_names=['get']),
         name='metadata-static-list'),
    path('config/', view=ConfigAPIView.as_view(http_method_names=['get']),
         name='config-list'),
    path(r'', include(router.urls)),
]
