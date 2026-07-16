from rest_framework import permissions

from donor_reporting_portal.apps.report_metadata.models import Donor, SecondaryDonor

NO_DONOR = "Various"


class DonorPermission(permissions.BasePermission):
    @staticmethod
    def _get_instances(view, query_params, mapping_dict, model):
        for field_name, qs_param in mapping_dict.items():
            values = view.kwargs.get(qs_param, query_params.get(qs_param, None))
            values = values.split(",") if values else []
            if values:
                filter_dict = {field_name + "__in": values}
                instances = list(model.objects.filter(**filter_dict).distinct())
                if instances:
                    return instances
        return []

    def _get_donors(self, view, query_params):
        mapping_dict = {"id": "donor_id", "code": "donor_code"}
        return self._get_instances(view, query_params, mapping_dict, Donor)

    def _get_secondary_donors(self, view, query_params):
        mapping_dict = {"id": "secondary_donor_id", "code": "secondary_donor_code"}
        return self._get_instances(view, query_params, mapping_dict, SecondaryDonor)

    def has_permission(self, request, view):
        user = request.user
        if NO_DONOR in request.query_params.values() or user.has_perm("roles.is_unicef_user"):
            return True
        donors = self._get_donors(view, request.query_params)
        secondary_donors = self._get_secondary_donors(view, request.query_params)
        if not donors:
            return False
        for donor in donors:
            context_object = (donor, secondary_donors[0]) if secondary_donors else donor
            if user.has_perm("roles.can_view_all_donors") or user.has_perm(
                "report_metadata.view_donor", context_object
            ):
                return True
        return False


class PublicLibraryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and view.is_public()
