from django.test.utils import override_settings
from django.urls import reverse

import pytest
from drf_api_checker.pytest import contract

from api_checker import LastModifiedRecorder
from freezegun import freeze_time


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
