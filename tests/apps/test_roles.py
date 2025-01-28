from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from donor_reporting_portal.apps.roles.models import UserRole
from factories import GroupFactory, UserRoleFactory


def test_admin_userrole(django_app, admin_user, userrole, donor, group, secondary_donor):
    assert str(userrole) is not None
    userrole_secondary_donor = UserRoleFactory(
        user=admin_user, donor=donor, group=group, secondary_donor=secondary_donor
    )
    assert str(userrole_secondary_donor) is not None
    url = reverse("admin:roles_userrole_changelist")
    response = django_app.get(url, user=admin_user)
    assert response


def test_manager_by_donor(logged_user, donor, group):
    assert UserRole.objects.get_permissions_by_donor(logged_user, donor).count() == 0
    UserRoleFactory(user=logged_user, donor=donor, group=group)
    assert UserRole.objects.get_permissions_by_donor(logged_user, donor).count() == 1


def test_manager_by_donor_secondary_donor(logged_user, donor, group, secondary_donor):
    assert UserRole.objects.get_permissions_by_donor_secondary_donor(logged_user, donor, secondary_donor).count() == 0
    UserRoleFactory(user=logged_user, donor=donor, group=group, secondary_donor=secondary_donor)
    assert UserRole.objects.get_permissions_by_donor(logged_user, donor).count() == 0
    assert UserRole.objects.get_permissions_by_donor_secondary_donor(logged_user, donor, secondary_donor).count() == 1


def test_manager_by_permissions(logged_user, donor, secondary_donor):
    ContentType.objects.first()
    content_type = ContentType.objects.get(model="donor", app_label="report_metadata")
    perm = Permission.objects.get(content_type=content_type, codename="view_donor")
    group = GroupFactory(permissions=(perm,))
    UserRoleFactory(user=logged_user, donor=donor, group=group, secondary_donor=secondary_donor)
    assert UserRole.objects.by_permissions("report_metadata.view_donor").count() == 1
    assert UserRole.objects.by_permissions(["report_metadata.view_donor", "roles.add_userrole"]).count() == 0
