from rest_framework import permissions

from donor_reporting_portal.apps.report_metadata.models import Donor, SecondaryDonor


class DonorPermission(permissions.BasePermission):

    @staticmethod
    def _get_instance(view, query_params, user, mapping_dict, model):
        instance = None
        for field_name, qs_param in mapping_dict.items():
            values = view.kwargs.get(qs_param, query_params.get(qs_param, None))
            values = values.split(',') if values else []
            filter_dict = {field_name + '__in': values, 'roles__user__pk': user.pk}
            if not instance:
                instance = model.objects.filter(**filter_dict).first()
        return instance

    def _get_donor(self, view, query_params, user):
        mapping_dict = {'id': 'donor_id', 'code': 'donor_code'}
        return self._get_instance(view, query_params, user, mapping_dict, Donor)

    def _get_secondary_donor(self, view, query_params, user):
        mapping_dict = {'id': 'secondary_donor_id', 'code': 'secondary_donor_code'}
        return self._get_instance(view, query_params, user, mapping_dict, SecondaryDonor)

    def has_permission(self, request, view):
        user = request.user
        donor = self._get_donor(view, request.query_params, user)
        secondary_donor = self._get_secondary_donor(view, request.query_params, user)
        context_object = (donor, secondary_donor) if donor and secondary_donor else donor
        if donor and user.has_perm('roles.can_view_all_donors') or \
                user.has_perm('report_metadata.view_donor', context_object):
            return True
        return False


class PublicLibraryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and view.is_public():
            return True
        return False
