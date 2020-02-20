from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from donor_reporting_portal.api.filters import (
    DonorFilter,
    ExternalGrantFilter,
    GrantFilter,
    SecondaryDonorFilter,
    ThemeFilter,
)
from donor_reporting_portal.api.permissions import DonorPermission
from donor_reporting_portal.api.serializers.metadata import (
    DonorSecondaryDonorSerializer,
    DonorSerializer,
    ExternalGrantSerializer,
    GrantSerializer,
    SecondaryDonorSerializer,
    ThemeSerializer,
)
from donor_reporting_portal.api.views.base import GenericAbstractViewSetMixin
from donor_reporting_portal.apps.report_metadata.models import Donor, ExternalGrant, Grant, SecondaryDonor, Theme
from donor_reporting_portal.apps.roles.models import UserRole


class AllowedDonorMixin:
    model = None
    permission_classes = (DonorPermission, )

    def get_queryset(self):
        donor_id = self.kwargs.get('donor_id', None)
        secondary_donor_code = self.request.GET.get('secondary_donor_code', None)
        qs = self.model.objects.filter(donor_id=donor_id)
        if secondary_donor_code:
            qs = qs.filter(secondarydonor__code=secondary_donor_code)
        return qs


class ThemeViewSet(GenericAbstractViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    filterset_class = ThemeFilter
    search_fields = ('name', )


class DonorViewSet(GenericAbstractViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Donor.objects.all()
    serializer_class = DonorSerializer
    filterset_class = DonorFilter
    search_fields = ('name', 'code')

    def retrieve(self, *args, **kwargs):
        self.serializer_class = DonorSecondaryDonorSerializer
        return viewsets.ModelViewSet.retrieve(self, *args, **kwargs)

    def get_permissions(self):
        if self.action in ('my_donors', 'my_admin_donors'):
            return IsAuthenticated(),
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def my_donors(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if not request.user.has_perm('roles.can_view_all_donors'):
            roles = UserRole.objects.by_permissions('report_metadata.view_donor').filter(user=request.user)
            qs = qs.filter(roles__in=roles)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_admin_donors(self, request, *args, **kwargs):
        roles = UserRole.objects.by_permissions(['report_metadata.view_donor',
                                                 'roles.add_userrole']).filter(user=request.user)
        serializer = self.get_serializer(self.get_queryset().filter(roles__in=roles), many=True)
        return Response(serializer.data)


class ExternalGrantViewSet(AllowedDonorMixin, GenericAbstractViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = ExternalGrant
    serializer_class = ExternalGrantSerializer
    filterset_class = ExternalGrantFilter
    search_fields = ('code', 'donor__name')


class GrantViewSet(AllowedDonorMixin, GenericAbstractViewSetMixin, viewsets.ReadOnlyModelViewSet):
    model = Grant
    serializer_class = GrantSerializer
    filterset_class = GrantFilter
    search_fields = ('code', 'donor__name')


class SecondaryDonorViewSet(GenericAbstractViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = SecondaryDonor.objects.all()
    serializer_class = SecondaryDonorSerializer
    filterset_class = SecondaryDonorFilter
    search_fields = ('name', 'code')
