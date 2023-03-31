from django.urls import reverse


def test_admin_userrole(django_app, admin_user, userrole):
    assert str(userrole) is not None
    url = reverse("admin:roles_userrole_changelist")
    response = django_app.get(url, user=admin_user)
    assert response
