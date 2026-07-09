from django.test import override_settings

import pytest

from perms import user_grant_role_permission


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


@pytest.mark.django_db
@override_settings(AUTHENTICATION_BACKENDS=("donor_reporting_portal.apps.core.backends.DonorRoleBackend",))
def test_donor_role_tuple_context(userrole):
    from django.contrib.auth.models import Permission

    from factories import SecondaryDonorFactory
    from donor_reporting_portal.apps.roles.models import UserRole

    perm = Permission.objects.get(content_type__app_label="roles", codename="can_view_all_donors")
    userrole.group.permissions.add(perm)
    secondary_donor = SecondaryDonorFactory()
    UserRole.objects.create(
        user=userrole.user,
        group=userrole.group,
        donor=userrole.donor,
        secondary_donor=secondary_donor,
    )
    context = (userrole.donor, secondary_donor)
    assert userrole.user.has_perm("roles.can_view_all_donors", context) is True


@pytest.mark.django_db
@override_settings(AUTHENTICATION_BACKENDS=("donor_reporting_portal.apps.core.backends.DonorRoleBackend",))
def test_donor_role_anonymous(db):
    from django.contrib.auth.models import AnonymousUser

    from factories import DonorFactory

    anon = AnonymousUser()
    donor = DonorFactory()
    assert not anon.has_perm("roles.can_view_all_donors", donor)


@pytest.mark.django_db
@override_settings(AUTHENTICATION_BACKENDS=("donor_reporting_portal.apps.core.backends.DonorRoleBackend",))
def test_donor_role_invalid_context(userrole):
    assert not userrole.user.has_perm("roles.can_view_all_donors", "invalid")
