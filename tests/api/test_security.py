from django.urls import reverse

import pytest
from drf_api_checker.pytest import contract, frozenfixture

from tests.api_checker import LastModifiedRecorder
from tests.factories import BusinessAreaFactory, UserFactory, UserRoleFactory


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
    return reverse('api:user-list')


@contract(recorder_class=LastModifiedRecorder)
def test_api_user_profile(request, django_app, logged_user, userrole):
    return reverse('api:user-my-profile')


@contract(recorder_class=LastModifiedRecorder)
def test_api_userrole_list(request, django_app, logged_user, userrole):
    return reverse('api:userrole-list')


@pytest.mark.django_db
@contract(LastModifiedRecorder)
def test_api_business_area_list(request, django_app, business_area):
    return reverse('api:businessarea-list')


@pytest.mark.django_db
@contract(LastModifiedRecorder)
def test_api_static(request, django_app):
    return reverse('api:dropdown-static-list')
