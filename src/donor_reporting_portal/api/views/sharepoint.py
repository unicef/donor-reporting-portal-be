from django.http import Http404, HttpResponse, HttpResponseBadRequest

from office365.runtime.client_request_exception import ClientRequestException
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ErrorDetail
from rest_framework.permissions import IsAuthenticated

from donor_reporting_portal.api.filters import SharePointLibraryFilter
from donor_reporting_portal.api.serializers.metadata import SharePointLibrarySerializer, SharePointSiteSerializer
from donor_reporting_portal.api.serializers.sharepoint import SharePointFileSerializer, SharePointItemSerializer
from donor_reporting_portal.api.views.base import GenericAbstractViewSetMixin
from donor_reporting_portal.apps.sharepoint.models import SharePointLibrary, SharePointSite
from donor_reporting_portal.libraries.sharepoint.client import SharePointClient, SharePointClientException
from donor_reporting_portal.libraries.sharepoint.file import SharePointFile


class AbstractSharePointViewSet(GenericAbstractViewSetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated, )  # DonorPermission

    lookup_field = 'filename'

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.site_name = self.kwargs.get('site_name')
        self.folder_name = self.kwargs.get('folder_name')
        dl = SharePointLibrary.objects.get(name=self.folder_name, site__name=self.site_name)
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
            self.client = SharePointClient(**dl_info)
        except SharePointClientException:
            raise HttpResponseBadRequest

    def get_serializer_context(self):
        return {
            'site_name': self.site_name,
            'folder_name': self.folder_name
        }

    def get_queryset(self):
        kwargs = self.request.query_params.dict()
        try:
            return self.client.read_files(filters=kwargs)
        except ClientRequestException:
            raise Http404

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if isinstance(exc, Http404):
            response.data['detail'] = ErrorDetail('No document found using selected filters', 'not_found')
        return response


class ItemSharePointViewSet(AbstractSharePointViewSet):
    serializer_class = SharePointItemSerializer

    def get_queryset(self):
        kwargs = self.request.query_params.dict()
        try:
            return self.client.read_items(filters=kwargs)
        except ClientRequestException:
            raise Http404


class FileSharePointViewSet(AbstractSharePointViewSet):
    serializer_class = SharePointFileSerializer

    lookup_field = 'filename'

    def get_object(self):
        filename = self.kwargs.get('filename', None)
        try:
            doc_file = self.client.read_file(filename)
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
    filter_class = SharePointLibraryFilter
