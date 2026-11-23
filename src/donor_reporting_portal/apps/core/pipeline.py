"""Social-auth pipeline steps specific to this project's User model."""

NAME_FIELDS = ("first_name", "last_name")


def ensure_user_names(details, user=None, *args, **kwargs):
    """Make sure first/last names are never ``None`` in the social pipeline."""
    normalized = dict(details or {})
    for field in NAME_FIELDS:
        if normalized.get(field) is None:
            current = getattr(user, field, None) if user else None
            normalized[field] = current if current is not None else ""

    result = {"details": normalized}
    for field in NAME_FIELDS:
        result[field] = normalized[field]
    return result
