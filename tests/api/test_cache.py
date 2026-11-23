from unittest import mock

from django.test import override_settings
from django.urls import reverse

import pytest
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory

from factories import DonorFactory, DRPMetadataFactory, UserFactory, UserRoleFactory
from donor_reporting_portal.api.cache import (
    REFERENCE_NAMESPACE,
    SOURCE_FILTERS_NAMESPACE,
    cache_key,
    permission_scope,
    scoped_get,
)
from donor_reporting_portal.api.views.config import ConfigAPIView
from donor_reporting_portal.api.views.static import MetadataStaticAPIView
from donor_reporting_portal.api.views.sharepoint import DRPGraphBasedSearchViewSet
from donor_reporting_portal.libs.cache import bump_generation, generation, get_or_compute, hash_parts
from sharepoint_rest_api.models import SourceId


def _request(query_params=None, user=None):
    query = "&".join(f"{key}={value}" for key, value in (query_params or {}).items())
    url = f"/?{query}" if query else "/"
    request = Request(APIRequestFactory().get(url))
    if user is not None:
        request.user = user
    return request


@pytest.mark.django_db
def test_permission_scope_isolated_by_donor_role():
    donor_a = DonorFactory()
    donor_b = DonorFactory()
    user_a = UserFactory()
    user_b = UserFactory()
    UserRoleFactory(user=user_a, donor=donor_a)
    UserRoleFactory(user=user_b, donor=donor_b)

    scope_a = permission_scope(_request({"donor_code": "X"}, user_a))
    scope_b = permission_scope(_request({"donor_code": "X"}, user_b))

    assert scope_a != scope_b


@pytest.mark.django_db
def test_permission_scope_stable_for_same_user():
    user = UserFactory()
    donor = DonorFactory()
    UserRoleFactory(user=user, donor=donor)

    first = permission_scope(_request({"donor_code": "X"}, user))
    second = permission_scope(_request({"donor_code": "X"}, user))

    assert first == second


def test_bump_generation_changes_cache_key():
    request = _request({"donor_code": "X"})
    before = cache_key(REFERENCE_NAMESPACE, request)

    bump_generation(REFERENCE_NAMESPACE)

    assert cache_key(REFERENCE_NAMESPACE, request) != before


def test_get_or_compute_caches_value():
    calls = []

    def producer():
        calls.append(1)
        return {"value": 1}

    key = f"drp:test:{hash_parts('key')}"

    assert get_or_compute(key, producer) == {"value": 1}
    assert get_or_compute(key, producer) == {"value": 1}
    assert len(calls) == 1


@pytest.mark.django_db
def test_source_id_save_bumps_source_filters_generation():
    before = generation(SOURCE_FILTERS_NAMESPACE)

    SourceId.objects.create(source_id="signal-uuid", default_filters={})

    assert generation(SOURCE_FILTERS_NAMESPACE) == before + 1


@pytest.mark.django_db
def test_scoped_get_isolates_users():
    user_a = UserFactory()
    user_b = UserFactory()
    UserRoleFactory(user=user_a, donor=DonorFactory())
    UserRoleFactory(user=user_b, donor=DonorFactory())
    request_a = _request({"donor_code": "X"}, user_a)
    request_b = _request({"donor_code": "X"}, user_b)
    computed = []

    def producer():
        computed.append(1)
        return len(computed)

    assert scoped_get(request_a, REFERENCE_NAMESPACE, producer) == 1
    assert scoped_get(request_b, REFERENCE_NAMESPACE, producer) == 2
    assert len(computed) == 2


@pytest.mark.django_db
def test_static_payload_is_cached():
    user = UserFactory()
    view = MetadataStaticAPIView()
    request = _request({"param": "value"}, user)
    view.request = request

    with mock.patch.object(view, "_build_payload", wraps=view._build_payload) as build:
        first = view.get(request)
        second = view.get(request)

    assert build.call_count == 1
    assert first.data == second.data


@pytest.mark.django_db
def test_config_payload_is_cached():
    user = UserFactory()
    view = ConfigAPIView()
    request = _request({"param": "value"}, user)

    with override_settings(MATOMO_SITE_ID="first"):
        first = view.get(request)
    with override_settings(MATOMO_SITE_ID="second"):
        second = view.get(request)

    assert first.data["tracker"]["site_id"] == "first"
    assert second.data == first.data


@pytest.mark.django_db
def test_cached_viewsets_do_not_share_responses():
    donor = DonorFactory()
    metadata = DRPMetadataFactory()
    client = APIClient()
    client.force_authenticate(UserFactory(is_superuser=True))

    # Populate the shared reference cache from a different viewset first.
    metadata_response = client.get(reverse("api:drpmetadata-list"))
    assert metadata_response.json()[0]["description"] == metadata.description

    donor_response = client.get(reverse("api:donor-list"))
    assert donor_response.status_code == 200
    assert [row["id"] for row in donor_response.json()] == [donor.pk]


@pytest.mark.django_db
def test_graph_search_response_is_cached():
    user = UserFactory()
    request = _request({"donor_code": "I49901"}, user)
    view = DRPGraphBasedSearchViewSet()
    view.request = request
    view.action = "list"
    view.format_kwarg = None
    view.client = mock.Mock()
    view.client.search.return_value = ([{"Title": "report"}], 1)

    first = view.get_queryset()
    second = view.get_queryset()

    assert view.client.search.call_count == 1
    assert first == second == [{"Title": "report"}]
    assert view.total_rows == 1
