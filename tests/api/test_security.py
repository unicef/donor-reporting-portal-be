from django.urls import reverse

import pytest
from drf_api_checker.pytest import contract, frozenfixture

from api_checker import LastModifiedRecorder
from factories import BusinessAreaFactory, UserFactory, UserRoleFactory


@frozenfixture()
def user(request, db):
    return UserFactory()


@frozenfixture()
def userrole(request, user, db):
    return UserRoleFactory(user=user)


@frozenfixture()
def business_area(request, db):
    return BusinessAreaFactory()


@contract(recorder_class=LastModifiedRecorder)
def test_api_user_list(request, django_app, user):
    return reverse("api:user-list")


@contract(recorder_class=LastModifiedRecorder)
def test_api_user_profile(request, django_app, logged_user, userrole):
    return reverse("api:user-my-profile")


@contract(recorder_class=LastModifiedRecorder)
def test_api_userrole_list(request, django_app, logged_user, userrole):
    return reverse("api:userrole-list")


@pytest.mark.django_db
@contract(LastModifiedRecorder)
def test_api_business_area_list(request, django_app, business_area):
    return reverse("api:businessarea-list")


@pytest.mark.django_db
def test_userrole_delete_deletes_user_when_no_other_roles(db):
    from rest_framework.test import APIClient

    from donor_reporting_portal.apps.core.models import User

    admin = UserFactory(is_superuser=True)
    client = APIClient()
    client.force_authenticate(admin)

    userrole = UserRoleFactory()
    user_id = userrole.user.pk
    assert User.objects.filter(pk=user_id).exists()

    url = reverse("api:userrole-detail", kwargs={"pk": userrole.pk})
    response = client.delete(url)
    assert response.status_code == 204
    assert not User.objects.filter(pk=user_id).exists()
