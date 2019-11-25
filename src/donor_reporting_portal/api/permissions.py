from rest_framework import permissions

from donor_reporting_portal.apps.report_metadata.models import Donor


class DonorPermission(permissions.BasePermission):

    def get_object(self, view):
        donor_dict = {
            'id': 'donor_id',
            'name': 'name',
            'code': 'code',
        }
        for field_name, qs_param in donor_dict.items():
            filter_dict = {
                field_name: view.kwargs.get(qs_param, None)
            }
            donor = Donor.objects.filter(**filter_dict).first()
            if donor:
                return donor
        return None


    def has_permission(self, request, view):
        donor = self.get_object(view)
        user = request.user
        if donor and user.has_perm('roles.can_view_all_donors') or user.has_perm('report_metadata.view_donor', donor):
            return True
        return False
