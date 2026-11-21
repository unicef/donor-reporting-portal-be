import hashlib
import json
from contextlib import nullcontext

from django.core.cache import cache

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


def cache_lock(key, timeout=10):
    lock = getattr(cache, "lock", None)
    return lock(key, timeout=timeout) if lock else nullcontext()


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
