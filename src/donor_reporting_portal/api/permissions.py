from django.conf import settings

from rest_framework import permissions

from donor_reporting_portal.apps.report_metadata.models import Donor, SecondaryDonor

NO_DONOR = "Various"


def is_open_donor(donor_code):
    """Return True when the requested donor code marks an open (``Various``) file."""
    if not donor_code:
        return False
    return NO_DONOR in [code.strip() for code in str(donor_code).split(",")]


class DonorPermission(permissions.BasePermission):
    @staticmethod
    def _get_instances(view, query_params, mapping_dict, model):
        instances = []
        for field_name, qs_param in mapping_dict.items():
            values = []
            for source in (view.kwargs.get(qs_param), query_params.get(qs_param)):
                if source:
                    values.extend(str(source).split(","))
            if values:
                instances.extend(model.objects.filter(**{f"{field_name}__in": values}).distinct())
        return instances

    def _get_donors(self, view, query_params):
        return self._get_instances(view, query_params, {"id": "donor_id", "code": "donor_code"}, Donor)

    def _get_secondary_donors(self, view, query_params):
        return self._get_instances(
            view,
            query_params,
            {"id": "secondary_donor_id", "code": "secondary_donor_code"},
            SecondaryDonor,
        )

    def has_permission(self, request, view):
        user = request.user
        if is_open_donor(request.query_params.get("donor_code")):
            return True
        if user.has_perm("roles.is_unicef_user") or user.has_perm("roles.can_view_all_donors"):
            return True
        donors = self._get_donors(view, request.query_params)
        if not donors:
            return False
        secondary_donors = self._get_secondary_donors(view, request.query_params)
        contexts = (
            [(donor, secondary) for donor in donors for secondary in secondary_donors] if secondary_donors else donors
        )
        return any(user.has_perm("report_metadata.view_donor", context) for context in contexts)


class SourceTierPermission(permissions.BasePermission):
    """Restrict internal and pooled-internal sources to UNICEF users."""

    def has_permission(self, request, view):
        source_id = request.query_params.get("source_id")
        if not source_id:
            return True
        source_ids = settings.DRP_SOURCE_IDS
        if source_id in (source_ids.get("internal"), source_ids.get("pool_internal")):
            return request.user.has_perm("roles.is_unicef_user")
        return True


class PublicLibraryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and view.is_public()
