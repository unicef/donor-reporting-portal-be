from django.contrib.auth.backends import ModelBackend

from donor_reporting_portal.apps.report_metadata.models import Donor
from donor_reporting_portal.apps.roles.models import UserRole


class DonorRoleBackend(ModelBackend):
    """Backend with check if a user has a specific permission on a given Donor"""

    # def has_perm(self, user_obj, perm, donor_obj):
    #     if user_obj.is_superuser:  # pragma: no cover
    #         return True
    #     if not user_obj.is_active or user_obj.is_anonymous:
    #         return set()
    #     perms = UserRole.objects.get_permissions_by_donor(user_obj, donor_obj)
    #     return perm in {f'{app_label}.{perm_name}' for app_label, perm_name in perms}

    def has_perm(self, user_obj, perm, context_obj):
        if user_obj.is_superuser:  # pragma: no cover
            return True
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()
        if isinstance(context_obj, Donor):
            perms = UserRole.objects.get_permissions_by_donor(user_obj, context_obj)
        elif isinstance(context_obj, tuple):
            donor_obj = context_obj[0]
            secondary_donor_obj = context_obj[-1]
            donor_perm = UserRole.objects.get_permissions_by_donor(user_obj, donor_obj)
            donor_secondary_donor_perm = UserRole.objects.get_permissions_by_donor_secondary_donor(
                user_obj, donor_obj, secondary_donor_obj
            )
            perms = donor_perm | donor_secondary_donor_perm
        else:
            return set()
        return perm in {f"{app_label}.{perm_name}" for app_label, perm_name in perms}
