from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.urls import reverse

from social_core.backends.azuread_b2c import AzureADB2COAuth2

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


class UnicefAzureADBBCOAuth2(AzureADB2COAuth2):
    """Unicef Azure ADB2C Custom Backend"""

    name = 'unicef-azuread-b2c-oauth2'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redirect_uri = settings.HOST + reverse('social:complete', kwargs={'backend': 'unicef-azuread-b2c-oauth2'})
