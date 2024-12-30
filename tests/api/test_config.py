from django.urls import reverse

import pytest
from drf_api_checker.pytest import contract

from api_checker import LastModifiedRecorder
from freezegun import freeze_time


@pytest.mark.django_db
@contract(LastModifiedRecorder)
@freeze_time("2025-01-01")
def test_api_metadata_static(request, django_app):
    return reverse("api:metadata-static-list")


@pytest.mark.django_db
@contract(LastModifiedRecorder)
def test_api_config(request, django_app):
    return reverse("api:config-list")
