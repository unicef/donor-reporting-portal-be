from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from django_filters import rest_framework as filters
from unicef_security.models import BusinessArea

from donor_reporting_portal.apps.report_metadata.models import Donor, ExternalGrant, Grant, Theme
from donor_reporting_portal.apps.roles.models import UserRole
from donor_reporting_portal.apps.sharepoint.models import SharePointLibrary


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


class SharePointLibraryFilter(filters.FilterSet):

    class Meta:
        model = SharePointLibrary
        fields = {
            'site': ['exact', 'in'],
            'active': ['exact', ],
        }
