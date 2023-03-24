from django.test import override_settings

import pytest

from tests.perms import user_grant_role_permission


@pytest.mark.django_db
@override_settings(AUTHENTICATION_BACKENDS=("donor_reporting_portal.apps.core.backends.DonorRoleBackend",))
def test_donor_role_superuser(admin_user, donor):
    assert admin_user.has_perm("any", donor)


@pytest.mark.django_db
@override_settings(AUTHENTICATION_BACKENDS=("donor_reporting_portal.apps.core.backends.DonorRoleBackend",))
def test_donor_role_inactive(userrole):
    with user_grant_role_permission(userrole.user, userrole.donor, permissions=["roles.can_view_all_donors"]):
        userrole.user.is_active = False
        userrole.user.save()
        assert not userrole.user.has_perm("roles.can_view_all_donors", userrole.donor)


@pytest.mark.django_db
@override_settings(AUTHENTICATION_BACKENDS=("donor_reporting_portal.apps.core.backends.DonorRoleBackend",))
def test_donor_role_ok(userrole):
    with user_grant_role_permission(userrole.user, userrole.donor, permissions=["roles.can_view_all_donors"]):
        assert userrole.user.has_perm("roles.can_view_all_donors", userrole.donor)
