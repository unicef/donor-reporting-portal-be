from rest_framework import permissions

from donor_reporting_portal.apps.report_metadata.models import Donor, SecondaryDonor


class DonorPermission(permissions.BasePermission):

    def get_donors(self, view, query_paramas):
        donor = secondary_donor = None
        donor_info = {'id': 'donor_id', 'code': 'donor_code'}
        secondary_donor_info = {'id': 'secondary_donor_id', 'code': 'secondary_donor_code'}

        for field_name, qs_param in donor_info.items():
            value = view.kwargs.get(qs_param, query_paramas.get(qs_param, None))
            filter_dict = {field_name: value}
            if not donor:
                donor = Donor.objects.filter(**filter_dict).first()

        for field_name, qs_param in secondary_donor_info.items():
            value = view.kwargs.get(qs_param, query_paramas.get(qs_param, None))
            filter_dict = {field_name: value}
            if not secondary_donor:
                secondary_donor = SecondaryDonor.objects.filter(**filter_dict).first()
        return donor, secondary_donor

    def has_permission(self, request, view):
        donor, secondary_donor = self.get_donors(view, request.query_params)
        user = request.user
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
