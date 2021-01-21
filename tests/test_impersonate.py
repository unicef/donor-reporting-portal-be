from unittest.mock import Mock

from donor_reporting_portal.libs.impersonate import queryset


def test_queryset(admin_user, user):
    assert queryset(Mock(user=admin_user))
