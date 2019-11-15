from rest_framework import permissions

from donor_reporting_portal.apps.report_metadata.models import Donor


class DonorPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        donor_id = view.kwargs.get('donor_id', None)
        donor = Donor.objects.filter(id=donor_id).first()
        user = request.user
        if donor and user.has_perm('roles.can_view_all_donors') or user.has_perm('report_metadata.view_donor', donor):
            return True
        return False
