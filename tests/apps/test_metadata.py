from unittest import mock

from django.urls import reverse


def test_admin_theme(django_app, admin_user, theme):
    assert str(theme) is not None
    url = reverse("admin:report_metadata_theme_changelist")
    response = django_app.get(url, user=admin_user)
    assert response


def test_admin_donor(django_app, admin_user, donor):
    assert str(donor) is not None
    url = reverse("admin:report_metadata_donor_changelist")
    response = django_app.get(url, user=admin_user)
    assert response


def test_admin_externalgrant(django_app, admin_user, external_grant):
    assert str(external_grant) is not None
    url = reverse("admin:report_metadata_externalgrant_changelist")
    response = django_app.get(url, user=admin_user)
    assert response


def test_admin_grant(django_app, admin_user, grant):
    assert str(grant) is not None
    url = reverse("admin:report_metadata_grant_changelist")
    response = django_app.get(url, user=admin_user)
    assert response


def test_grant_sync_url(django_app, admin_user):
    with mock.patch("donor_reporting_portal.apps.report_metadata.admin.grant_sync"):
        url = "/admin/report_metadata/externalgrant/_sync_grants/"
        response = django_app.get(url, user=admin_user)
        assert response
