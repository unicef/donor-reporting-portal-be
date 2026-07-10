from unittest import mock

import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from donor_reporting_portal.api.permissions import DonorPermission, PublicLibraryPermission
from perms import user_grant_permissions


class TestDonorPermission:
    @pytest.mark.django_db
    def test_no_donor_in_query_params(self):
        perm = DonorPermission()
        factory = APIRequestFactory()
        request = Request(factory.get("/?donor_code=Various"))
        view = mock.Mock(kwargs={})
        assert perm.has_permission(request, view) is True

    @pytest.mark.django_db
    def test_unicef_user(self, user):
        perm = DonorPermission()
        factory = APIRequestFactory()
        request = Request(factory.get("/?donor_code=test"))
        request.user = user
        view = mock.Mock(kwargs={})
        with user_grant_permissions(user, permissions=["roles.is_unicef_user"]):
            assert perm.has_permission(request, view) is True

    @pytest.mark.django_db
    def test_donor_not_found(self, user):
        perm = DonorPermission()
        factory = APIRequestFactory()
        request = Request(factory.get("/?donor_code=nonexistent"))
        request.user = user
        view = mock.Mock(kwargs={})
        assert perm.has_permission(request, view) is False


class TestPublicLibraryPermission:
    @pytest.mark.django_db
    def test_authenticated_and_public_view(self, user):
        perm = PublicLibraryPermission()
        factory = APIRequestFactory()
        request = Request(factory.get("/"))
        request.user = user
        view = mock.Mock()
        view.is_public = mock.Mock(return_value=True)
        assert perm.has_permission(request, view) is True

    def test_unauthenticated_user(self):
        perm = PublicLibraryPermission()
        factory = APIRequestFactory()
        request = Request(factory.get("/"))
        request.user = AnonymousUser()
        view = mock.Mock()
        view.is_public = mock.Mock(return_value=True)
        assert perm.has_permission(request, view) is False
