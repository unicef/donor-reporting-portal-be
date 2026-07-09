from donor_reporting_portal import NAME, VERSION
from donor_reporting_portal.apps.core.checks import check_imports


def test_imports():
    check_imports()


def test_version_tag():
    from donor_reporting_portal.apps.core.templatetags.core import version

    result = version()
    assert NAME in result
    assert VERSION in result
