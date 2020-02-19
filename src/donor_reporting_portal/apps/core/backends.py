from django.contrib.auth.backends import ModelBackend

from donor_reporting_portal.apps.roles.models import UserRole


class DonorRoleBackend(ModelBackend):
    """Backend with check if a user has a specific permission on a given Donor"""

    def has_perm(self, user_obj, perm, donor_obj):
        if user_obj.is_superuser:  # pragma: no cover
            return True
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()
        perms = UserRole.objects.get_permissions_by_donor(user_obj, donor_obj)
        return perm in {f'{app_label}.{perm_name}' for app_label, perm_name in perms}
