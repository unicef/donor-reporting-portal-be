from django.urls import reverse

from drf_api_checker.pytest import contract, frozenfixture

from tests.api_checker import ExpectedErrorRecorder, LastModifiedRecorder
from tests.factories import (
    DonorFactory,
    DRPMetadataFactory,
    ExternalGrantFactory,
    GrantFactory,
    ThemeFactory,
    UserRoleFactory,
)
from tests.perms import user_grant_permissions, user_grant_role_permission


@frozenfixture()
def userrole(request, db, logged_user):
    return UserRoleFactory(user=logged_user)


@frozenfixture()
def theme(request, db):
    return ThemeFactory()


@frozenfixture()
def donor(request, db):
    return DonorFactory()


@frozenfixture()
def external_grant(request, db):
    return ExternalGrantFactory()


@frozenfixture()
def grant(
    request,
    db,
):
    return GrantFactory()


@frozenfixture()
def metadata(
    request,
    db,
):
    return DRPMetadataFactory()


@contract(recorder_class=LastModifiedRecorder)
def test_api_theme_list(request, django_app, logged_user, theme):
    return reverse("api:theme-list")


@contract(recorder_class=LastModifiedRecorder)
def test_api_donor_list(request, django_app, logged_user, donor):
    return reverse("api:donor-list")


@contract(recorder_class=LastModifiedRecorder)
def test_api_my_donor_list_unicef_user(request, django_app, logged_user, donor):
    with user_grant_permissions(logged_user, permissions=["roles.can_view_all_donors"]):
        return reverse("api:donor-my-donors")


@contract(recorder_class=LastModifiedRecorder)
def test_api_my_donor_list_donor(request, django_app, logged_user, donor):
    with user_grant_role_permission(logged_user, donor, permissions=["report_metadata.view_donor"]):
        return reverse("api:donor-my-donors")


@contract(recorder_class=ExpectedErrorRecorder)
def test_api_my_donor_list_fail(request, django_app, logged_user, donor):
    return reverse("api:donor-my-donors")


@contract(recorder_class=ExpectedErrorRecorder)
def test_api_my_admin_donor_list_donor_fail(request, django_app, logged_user, donor):
    return reverse("api:donor-my-admin-donors")


def test_api_external_grant_list(request, django_app, logged_user, external_grant):
    return reverse("api:external_grant-list", kwargs={"donor_id": external_grant.donor.pk})


def test_api_grant_list(request, django_app, logged_user, grant):
    return reverse("api:grant-list", kwargs={"donor_id": grant.donor.pk})


@contract(recorder_class=LastModifiedRecorder)
def test_metadata_list(request, django_app, logged_user, metadata):
    return reverse("api:drpmetadata-list")
