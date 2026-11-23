from unittest import mock

from unicef_security.pipeline import create_unicef_user, user_details

from donor_reporting_portal.apps.core.pipeline import ensure_user_names


def test_ensure_user_names_defaults_missing_names_to_empty_string():
    details = {"email": "khumagai@unicef.org", "first_name": None, "last_name": None}

    result = ensure_user_names(details=details)

    assert result["details"]["first_name"] == ""
    assert result["details"]["last_name"] == ""
    assert details["first_name"] is None  # input is not mutated


def test_ensure_user_names_preserves_known_user_names():
    user = mock.Mock(first_name="Kengo", last_name="Khumagai")

    result = ensure_user_names(details={"first_name": None, "last_name": None}, user=user)

    assert result["details"]["first_name"] == "Kengo"
    assert result["details"]["last_name"] == "Khumagai"


def test_ensure_user_names_keeps_provider_names():
    details = {"first_name": "Kengo", "last_name": "Khumagai"}

    result = ensure_user_names(details=details)

    assert result["details"]["first_name"] == "Kengo"
    assert result["details"]["last_name"] == "Khumagai"


def test_create_unicef_user_with_missing_name_claims():
    backend = mock.Mock()
    backend.setting.return_value = ["username", "email", "first_name", "last_name"]
    strategy = mock.Mock()
    strategy.create_user.return_value = "created-user"
    details = {
        "username": "khumagai@unicef.org",
        "email": "khumagai@unicef.org",
        "first_name": None,
        "last_name": None,
    }

    normalized = ensure_user_names(details=details)["details"]
    result = create_unicef_user(
        strategy,
        normalized,
        backend,
        response={"email": "khumagai@unicef.org"},
    )

    assert result == {"is_new": True, "user": "created-user"}
    kwargs = strategy.create_user.call_args.kwargs
    assert kwargs["first_name"] == ""
    assert kwargs["last_name"] == ""


def test_user_details_with_missing_name_claims():
    strategy = mock.Mock()
    strategy.setting.side_effect = lambda name, default=None, **kwargs: default
    backend = mock.Mock(ASSOCIATION_ONLY=False)
    user = mock.Mock(first_name=None, last_name=None)
    details = {"first_name": None, "last_name": None}

    normalized = ensure_user_names(details=details, user=user)["details"]
    user_details(strategy, normalized, backend, user=user)

    assert user.first_name == ""
    assert user.last_name == ""
    user.save.assert_called_once_with()
