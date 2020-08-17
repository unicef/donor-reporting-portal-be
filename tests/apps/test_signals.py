from django.contrib.auth import get_user_model

import pytest

from tests.factories import GroupFactory


@pytest.mark.django_db
def test_assign_to_unicef_group_ok():
    GroupFactory(name='UNICEF User')
    user = get_user_model().objects.create(username='user@unicef.org', email='user@unicef.org')
    assert user.groups.count() == 1
    assert user.groups.first().name == 'UNICEF User'


@pytest.mark.django_db
def test_assign_to_unicef_group_ko():
    GroupFactory(name='UNICEF User')
    user = get_user_model().objects.create(username='user@wfp.org', email='user@wfp.org')
    assert user.groups.count() == 0
