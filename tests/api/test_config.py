from django.test.utils import override_settings
from django.urls import reverse

import pytest
from drf_api_checker.pytest import contract
from rest_framework.test import APIClient

from api_checker import LastModifiedRecorder
from freezegun import freeze_time

from factories import UserFactory


ALL_NULL_SOURCE_IDS = {
    "internal": None,
    "external": None,
    "pool_internal": None,
    "pool_external": None,
    "thematic_internal": None,
    "thematic_external": None,
    "gavi": None,
    "gavi_soa": None,
}


@pytest.mark.django_db
@freeze_time("2025-01-01")
@override_settings(DRP_SOURCE_IDS=ALL_NULL_SOURCE_IDS)
@contract(LastModifiedRecorder)
def test_api_metadata_static(request, django_app):
    return reverse("api:metadata-static-list")


@pytest.mark.django_db
@override_settings(DRP_SOURCE_IDS=ALL_NULL_SOURCE_IDS)
@contract(LastModifiedRecorder)
def test_api_config(request, django_app):
    return reverse("api:config-list")


@pytest.mark.django_db
@override_settings(DRP_SOURCE_IDS=ALL_NULL_SOURCE_IDS)
def test_api_metadata_static_non_unicef_user():
    user = UserFactory(email="external@partner.org", is_superuser=False)
    client = APIClient()
    client.force_authenticate(user)
    url = reverse("api:metadata-static-list")
    response = client.get(url)
    assert response.status_code == 200
    categories = [c["code"] for c in response.data["donor_reporting_category"]]
    assert "input_report" not in categories
    docs = [d["code"] for d in response.data["donor_document"]]
    assert "input_report_-_final" not in docs
    assert "input_report_-_interim" not in docs
    assert "correspondence" not in docs
    assert "others" not in docs
    assert "note_for_the_record" not in docs
    assert "framework_agreement_checklist" not in docs
