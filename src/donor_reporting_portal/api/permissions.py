from rest_framework import permissions

from donor_reporting_portal.apps.report_metadata.models import Donor


class DonorPermission(permissions.BasePermission):

    def get_object(self, view, query_paramas):
        donor_dict = {
            'id': 'donor_id',
            'name': 'donor',
            'code': 'donor_code',
        }
        for field_name, qs_param in donor_dict.items():
            value = view.kwargs.get(qs_param, query_paramas.get(qs_param, None))
            filter_dict = {
                field_name: value
            }
            donor = Donor.objects.filter(**filter_dict).first()
            if donor:
                return donor
        return None

    def has_permission(self, request, view):
        donor = self.get_object(view, request.query_params)
        user = request.user
        if donor and user.has_perm('roles.can_view_all_donors') or \
                user.has_perm('report_metadata.view_donor', donor) or \
                view.kwargs.get('filename'):
            return True
        return False


class PublicLibraryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not view.get_library().require_donor_permission:
            return True
        return False
