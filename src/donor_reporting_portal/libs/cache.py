import hashlib
import json
from contextlib import contextmanager

from django.core.cache import cache
from redis.exceptions import LockNotOwnedError

DEFAULT_TIMEOUT = 300
GENERATION_KEY = "drp:gen:{namespace}"


def hash_parts(*parts):
    raw = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def generation(namespace):
    return cache.get(GENERATION_KEY.format(namespace=namespace), 1)


def bump_generation(namespace):
    key = GENERATION_KEY.format(namespace=namespace)
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, generation(namespace) + 1)


@contextmanager
def cache_lock(key, timeout=60, blocking_timeout=5):
    lock = getattr(cache, "lock", None)
    if not lock:
        yield
        return
    acquired = lock(key, timeout=timeout, blocking_timeout=blocking_timeout)
    try:
        with acquired:
            yield
    except LockNotOwnedError:
        # The lock expired or was taken over; do not release another worker's lock.
        pass


def get_or_compute(key, producer, timeout=DEFAULT_TIMEOUT):
    value = cache.get(key)
    if value is not None:
        return value
    with cache_lock(f"{key}:lock"):
        value = cache.get(key)
        if value is None:
            value = producer()
            cache.set(key, value, timeout)
    return value


def register_cache_signals():
    from django.db.models import signals  # noqa: PLC0415

    from donor_reporting_portal.apps.report_metadata.models import (  # noqa: PLC0415
        Donor,
        DRPMetadata,
        ExternalGrant,
        Grant,
        SecondaryDonor,
        Theme,
    )
    from donor_reporting_portal.apps.sharepoint.models import SharePointGroup  # noqa: PLC0415
    from sharepoint_rest_api.models import SourceId  # noqa: PLC0415

    def invalidate(namespace):
        def handler(**kwargs):
            bump_generation(namespace)

        return handler

    for model in (Donor, DRPMetadata, ExternalGrant, Grant, SecondaryDonor, Theme, SharePointGroup):
        for action in (signals.post_save, signals.post_delete):
            action.connect(invalidate("reference"), sender=model, weak=False)
    for action in (signals.post_save, signals.post_delete):
        action.connect(invalidate("source_filters"), sender=SourceId, weak=False)
