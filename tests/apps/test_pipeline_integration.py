import pytest
from django.conf import settings
from social_django.models import DjangoStorage
from social_django.strategy import DjangoStrategy

from donor_reporting_portal.apps.core.backends import UNICEFAzureADB2COAuth2


@pytest.mark.django_db
def test_pipeline_creates_user_when_b2c_omits_name_claims():
    """Regression: Azure AD B2C can return no given_name/family_name claims.

    ``USER_FIELDS`` includes the name columns, so passing ``None`` through the
    pipeline used to fail with a NOT NULL violation on ``core_user``.
    """
    strategy = DjangoStrategy(storage=DjangoStorage)
    backend = UNICEFAzureADB2COAuth2(strategy=strategy)
    response = {
        "sub": "integration-sub-missing-names",
        "email": "newuser@unicef.org",
        "name": None,
        "given_name": None,
        "family_name": None,
    }

    out = backend.run_pipeline(
        list(settings.SOCIAL_AUTH_PIPELINE),
        strategy=strategy,
        backend=backend,
        details={},
        response=response,
    )

    user = out["user"]
    user.refresh_from_db()
    assert user.username == "newuser@unicef.org"
    assert user.first_name == ""
    assert user.last_name == ""
