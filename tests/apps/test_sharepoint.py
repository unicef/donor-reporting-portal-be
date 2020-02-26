from django.urls import reverse


def test_admin_sharepoint_group(django_app, admin_user, sharepoint_group):
    assert str(sharepoint_group) is not None
    url = reverse('admin:sharepoint_sharepointgroup_changelist')
    response = django_app.get(url, user=admin_user)
    assert response
