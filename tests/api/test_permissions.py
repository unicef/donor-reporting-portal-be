from unittest import mock

import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from factories import DonorFactory
from donor_reporting_portal.api.permissions import DonorPermission, PublicLibraryPermission
from perms import user_grant_permissions, user_grant_role_permission


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

    @pytest.mark.django_db
    def test_single_donor_with_permission(self, user):
        donor = DonorFactory(code="D001")
        with user_grant_role_permission(user, donor, permissions=["report_metadata.view_donor"]):
            perm = DonorPermission()
            factory = APIRequestFactory()
            request = Request(factory.get("/?donor_code=D001"))
            request.user = user
            view = mock.Mock(kwargs={})
            assert perm.has_permission(request, view) is True

    @pytest.mark.django_db
    def test_single_donor_without_permission(self, user):
        DonorFactory(code="D001")
        perm = DonorPermission()
        factory = APIRequestFactory()
        request = Request(factory.get("/?donor_code=D001"))
        request.user = user
        view = mock.Mock(kwargs={})
        assert perm.has_permission(request, view) is False

    @pytest.mark.django_db
    def test_comma_separated_donors_all_authorized(self, user):
        donor1 = DonorFactory(code="D001")
        donor2 = DonorFactory(code="D002")
        donor3 = DonorFactory(code="D003")
        with user_grant_role_permission(user, donor1, permissions=["report_metadata.view_donor"]):
            with user_grant_role_permission(user, donor2, permissions=["report_metadata.view_donor"]):
                with user_grant_role_permission(user, donor3, permissions=["report_metadata.view_donor"]):
                    perm = DonorPermission()
                    factory = APIRequestFactory()
                    request = Request(factory.get("/?donor_code=D001,D002,D003"))
                    request.user = user
                    view = mock.Mock(kwargs={})
                    assert perm.has_permission(request, view) is True

    @pytest.mark.django_db
    def test_comma_separated_donors_partial_authorized(self, user):
        donor1 = DonorFactory(code="D001")
        DonorFactory(code="D002")
        DonorFactory(code="D003")
        with user_grant_role_permission(user, donor1, permissions=["report_metadata.view_donor"]):
            perm = DonorPermission()
            factory = APIRequestFactory()
            request = Request(factory.get("/?donor_code=D001,D002,D003"))
            request.user = user
            view = mock.Mock(kwargs={})
            assert perm.has_permission(request, view) is True

    @pytest.mark.django_db
    def test_comma_separated_donors_none_authorized(self, user):
        DonorFactory(code="D001")
        DonorFactory(code="D002")
        perm = DonorPermission()
        factory = APIRequestFactory()
        request = Request(factory.get("/?donor_code=D001,D002"))
        request.user = user
        view = mock.Mock(kwargs={})
        assert perm.has_permission(request, view) is False

    @pytest.mark.django_db
    def test_comma_separated_donors_can_view_all(self, user):
        DonorFactory(code="D001")
        DonorFactory(code="D002")
        DonorFactory(code="D003")
        with user_grant_permissions(user, permissions=["roles.can_view_all_donors"]):
            perm = DonorPermission()
            factory = APIRequestFactory()
            request = Request(factory.get("/?donor_code=D001,D002,D003"))
            request.user = user
            view = mock.Mock(kwargs={})
            assert perm.has_permission(request, view) is True

    @pytest.mark.django_db
    def test_comma_separated_donors_nonexistent(self, user):
        donor1 = DonorFactory(code="D001")
        with user_grant_role_permission(user, donor1, permissions=["report_metadata.view_donor"]):
            perm = DonorPermission()
            factory = APIRequestFactory()
            request = Request(factory.get("/?donor_code=D001,nonexistent"))
            request.user = user
            view = mock.Mock(kwargs={})
            assert perm.has_permission(request, view) is True


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
