from unittest import mock

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import override_settings
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from factories import DonorFactory
from donor_reporting_portal.api.permissions import DonorPermission, PublicLibraryPermission, SourceTierPermission
from donor_reporting_portal.api.views.sharepoint import DRPGraphBasedSearchViewSet
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

    @pytest.mark.django_db
    def test_various_in_unrelated_param_denied(self, user):
        DonorFactory(code="D001")
        perm = DonorPermission()
        factory = APIRequestFactory()
        request = Request(factory.get("/?search=Various&donor_code=D001"))
        request.user = user
        view = mock.Mock(kwargs={})
        assert perm.has_permission(request, view) is False

    @pytest.mark.django_db
    def test_various_within_donor_code_allowed(self, user):
        DonorFactory(code="D002")
        perm = DonorPermission()
        factory = APIRequestFactory()
        request = Request(factory.get("/?donor_code=D002,Various"))
        request.user = user
        view = mock.Mock(kwargs={})
        assert perm.has_permission(request, view) is True

    @pytest.mark.django_db
    def test_url_donor_does_not_hide_query_donor(self, user):
        donor1 = DonorFactory(code="D001")
        donor2 = DonorFactory(code="D002")
        with user_grant_role_permission(user, donor2, permissions=["report_metadata.view_donor"]):
            perm = DonorPermission()
            factory = APIRequestFactory()
            request = Request(factory.get("/?donor_code=D002"))
            request.user = user
            view = mock.Mock(kwargs={"donor_id": donor1.id})
            assert perm.has_permission(request, view) is True


class TestSourceTierPermission:
    @pytest.mark.django_db
    def test_internal_source_denied_without_unicef_permission(self, user):
        request = Request(APIRequestFactory().get("/?source_id=int-uuid"))
        request.user = user
        with override_settings(DRP_SOURCE_IDS={"internal": "int-uuid"}):
            assert SourceTierPermission().has_permission(request, mock.Mock()) is False

    @pytest.mark.django_db
    def test_internal_source_allowed_for_unicef_user(self, user):
        request = Request(APIRequestFactory().get("/?source_id=int-uuid"))
        request.user = user
        with user_grant_permissions(user, permissions=["roles.is_unicef_user"]):
            with override_settings(DRP_SOURCE_IDS={"internal": "int-uuid"}):
                assert SourceTierPermission().has_permission(request, mock.Mock()) is True

    @pytest.mark.django_db
    def test_thematic_source_allowed(self, user):
        request = Request(APIRequestFactory().get("/?source_id=thematic-uuid"))
        request.user = user
        with override_settings(DRP_SOURCE_IDS={"thematic_internal": "thematic-uuid"}):
            assert SourceTierPermission().has_permission(request, mock.Mock()) is True

    @pytest.mark.django_db
    def test_missing_source_id_allowed(self, user):
        request = Request(APIRequestFactory().get("/"))
        request.user = user
        assert SourceTierPermission().has_permission(request, mock.Mock()) is True

    @pytest.mark.django_db
    def test_donor_grant_cannot_reach_internal_source(self, user):
        donor = DonorFactory(code="D001")
        request = Request(APIRequestFactory().get("/?donor_code=D001&source_id=int-uuid"))
        request.user = user
        view = mock.Mock(kwargs={})
        view.is_public = mock.Mock(return_value=False)
        permission = DRPGraphBasedSearchViewSet.permission_classes[0]()
        with user_grant_role_permission(user, donor, permissions=["report_metadata.view_donor"]):
            with override_settings(DRP_SOURCE_IDS={"internal": "int-uuid"}):
                assert permission.has_permission(request, view) is False


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
