from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from django_filters import rest_framework as filters
from unicef_business_areas.models import BusinessArea

from donor_reporting_portal.apps.report_metadata.models import (
    Donor,
    DRPMetadata,
    ExternalGrant,
    Grant,
    SecondaryDonor,
    Theme,
)
from donor_reporting_portal.apps.roles.models import UserRole


class GroupFilter(filters.FilterSet):

    class Meta:
        model = Group
        fields = {
            'name': ['exact', 'icontains'],
        }


class UserFilter(filters.FilterSet):

    class Meta:
        model = get_user_model()
        fields = {
            'username': ['exact', 'icontains'],
            'last_name': ['exact', 'icontains'],
            'first_name': ['exact', 'icontains'],
        }


class UserRoleFilter(filters.FilterSet):

    class Meta:
        model = UserRole
        fields = {
            'donor': ['exact', 'in'],
            'group': ['exact', 'in'],
            'user': ['exact', 'in'],
            'secondary_donor': ['exact', 'in'],
            'notification_period': ['exact', 'in']
        }


class BusinessAreaFilter(filters.FilterSet):

    class Meta:
        model = BusinessArea
        fields = {
            'region': ['exact', 'in'],
            'country': ['exact', 'in'],
        }


class ThemeFilter(filters.FilterSet):
    class Meta:
        model = Theme
        fields = {
            'name': ['exact', 'in'],
        }


class DonorFilter(filters.FilterSet):
    class Meta:
        model = Donor
        fields = {
            'name': ['exact', 'in'],
            'code': ['exact', 'in'],
            'us_gov': ['exact'],
            'active': ['exact'],
        }


class ExternalGrantFilter(filters.FilterSet):
    class Meta:
        model = ExternalGrant
        fields = {
            'code': ['exact', 'in'],
            'donor': ['exact', 'in'],
        }


class GrantFilter(filters.FilterSet):
    business_areas__in = filters.BaseInFilter(field_name="business_areas")

    class Meta:
        model = Grant
        fields = {
            'donor': ['exact'],
            'code': ['exact', 'in'],
            'year': ['exact', 'in'],
            'theme': ['exact', 'in'],
            'business_areas': ['exact', 'in'],
            'expiry_date': ['lte', 'gte', 'gt', 'lt'],
            'financial_close_date': ['lte', 'gte', 'gt', 'lt'],
        }


class SecondaryDonorFilter(filters.FilterSet):
    grants__in = filters.BaseInFilter(field_name="grants")

    class Meta:
        model = SecondaryDonor
        fields = {
            'name': ['exact', 'in'],
            'code': ['exact', 'in'],
        }


class DRPMetadataFilter(filters.FilterSet):

    class Meta:
        model = DRPMetadata
        fields = {
            'category': ['exact', 'in'],
            'audience': ['exact', 'in'],
        }
