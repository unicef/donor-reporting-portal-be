from django.urls import reverse

import pytest
from drf_api_checker.pytest import contract

from tests.api_checker import LastModifiedRecorder


@pytest.mark.django_db
@contract(LastModifiedRecorder)
def test_api_metadata_static(request, django_app):
    return reverse('api:metadata-static-list')


@pytest.mark.django_db
@contract(LastModifiedRecorder)
def test_api_config(request, django_app):
    return reverse('api:config-list')
