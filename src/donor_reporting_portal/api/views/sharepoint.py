from django.core.cache import caches
from django.http import Http404, HttpResponse

from office365.runtime.client_request_exception import ClientRequestException
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ErrorDetail, PermissionDenied

from donor_reporting_portal.api.filters import SharePointLibraryFilter
from donor_reporting_portal.api.permissions import DonorPermission, PublicLibraryPermission
from donor_reporting_portal.api.serializers.metadata import SharePointLibrarySerializer, SharePointSiteSerializer
from donor_reporting_portal.api.serializers.sharepoint import SharePointFileSerializer, SharePointItemSerializer
from donor_reporting_portal.api.views.base import GenericAbstractViewSetMixin
from donor_reporting_portal.api.views.utils import get_cache_key
from donor_reporting_portal.apps.sharepoint.models import SharePointLibrary, SharePointSite
from donor_reporting_portal.libraries.sharepoint.client import SharePointClient, SharePointClientException
from donor_reporting_portal.libraries.sharepoint.file import SharePointFile

cache = caches['default']


class AbstractSharePointViewSet(GenericAbstractViewSetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = ((DonorPermission | PublicLibraryPermission),)

    def get_library(self):
        return SharePointLibrary.objects.get(name=self.folder_name, site__name=self.site_name)

    @property
    def client(self):
        key = self.get_cache_key(**{'client': 'client'})
        client = cache.get(key)
        if client is None:
            dl = self.get_library()
            dl_info = {
                'url': dl.site.site_url(),
                'relative_url': dl.site.relative_url(),
                'folder_name': dl.name
            }
            if dl.site.username:
                dl_info['username']: dl.site.username
            if dl.site.username:
                dl_info['password']: dl.site.password
            try:
                client = SharePointClient(**dl_info)
                cache.set(key, client)
            except SharePointClientException:
                raise PermissionDenied

        return client

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx.update({
            'site_name': self.site_name,
            'folder_name': self.folder_name
        })
        return ctx

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if isinstance(exc, Http404):
            response.data['detail'] = ErrorDetail('No document found using selected filters', 'not_found')
        return response

    @property
    def site_name(self):
        return self.kwargs.get('site_name')

    @property
    def folder_name(self):
        return self.kwargs.get('folder_name')

    def get_cache_key(self, **kwargs):
        key = get_cache_key([self.site_name, self.folder_name], **kwargs)
        return key


class ItemSharePointViewSet(AbstractSharePointViewSet):
    serializer_class = SharePointItemSerializer

    def get_queryset(self):
        kwargs = self.request.query_params.dict()
        try:
            key = self.get_cache_key(**kwargs)
            response = cache.get(key)
            if response is None:
                response = self.client.read_items(filters=kwargs)
                cache.set(key, response)
            return response
        except ClientRequestException:
            raise Http404


class ItemSharePointCamlViewSet(ItemSharePointViewSet):
    def get_queryset(self):
        kwargs = self.request.query_params.dict()
        cache_dict = kwargs.copy()
        cache_dict['caml'] = 'true'
        try:
            key = self.get_cache_key(**cache_dict)
            response = cache.get(key)
            if response is None:
                response = self.client.read_caml_items(filters=kwargs)
                cache.set(key, response)
            return response
        except ClientRequestException:
            raise Http404


class FileSharePointViewSet(AbstractSharePointViewSet):
    serializer_class = SharePointFileSerializer
    lookup_field = 'filename'

    def get_object(self):
        filename = self.kwargs.get('filename', None)
        try:
            filename, *extension = filename.split('__ext__')
            if extension and len(extension) == 1:
                extension = extension[0]
            else:
                extension = 'pdf'
            doc_file = self.client.read_file(f'{filename}.{extension}')
        except ClientRequestException:
            raise Http404
        return doc_file

    def get_queryset(self):
        kwargs = self.request.query_params.dict()
        try:
            return self.client.read_files(filters=kwargs)
        except ClientRequestException:
            raise Http404

    @action(detail=True, methods=['get'])
    def download(self, request, *args, **kwargs):
        sh_file = self.get_object()
        relative_url = sh_file.properties['ServerRelativeUrl']
        response = SharePointFile.open_binary(self.client.context, relative_url)

        django_response = HttpResponse(
            content=response.content,
            status=response.status_code,
            content_type=response.headers['Content-Type'],
        )
        django_response['Content-Disposition'] = 'attachment; filename=%s' % sh_file.properties['Name']
        return django_response


class SharePointSiteViewSet(GenericAbstractViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = SharePointSite.objects.all()
    serializer_class = SharePointSiteSerializer
    search_fields = ('name', )


class SharePointLibraryViewSet(GenericAbstractViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = SharePointLibrary.objects.all()
    serializer_class = SharePointLibrarySerializer
    search_fields = ('name', )
    filterset_class = SharePointLibraryFilter
