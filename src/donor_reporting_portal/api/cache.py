from django.conf import settings
from rest_framework.response import Response

from donor_reporting_portal.apps.roles.models import UserRole
from donor_reporting_portal.libs.cache import DEFAULT_TIMEOUT, generation, get_or_compute, hash_parts

REFERENCE_NAMESPACE = "reference"
SOURCE_FILTERS_NAMESPACE = "source_filters"
GRAPH_SEARCH_NAMESPACE = "graph_search"
STATIC_NAMESPACE = "static"
CONFIG_NAMESPACE = "config"


def source_tier(source_id):
    if not source_id:
        return "none"
    source_ids = settings.DRP_SOURCE_IDS
    if source_id in (source_ids.get("thematic_internal"), source_ids.get("thematic_external")):
        return "public"
    if source_id in (source_ids.get("internal"), source_ids.get("pool_internal")):
        return "restricted"
    return "other"


def permission_scope(request):
    user = request.user
    if not getattr(user, "is_authenticated", False):
        return "anonymous"
    roles = UserRole.objects.filter(user=user)
    attributes = {
        "superuser": bool(user.is_superuser),
        "unicef_permission": user.has_perm("roles.is_unicef_user"),
        "unicef_email": user.username.endswith("@unicef.org"),
        "all_donors": user.has_perm("roles.can_view_all_donors"),
        "tier": source_tier(request.query_params.get("source_id")),
        "donors": sorted(set(roles.exclude(donor=None).values_list("donor_id", flat=True))),
        "secondary_donors": sorted(
            set(roles.exclude(secondary_donor=None).values_list("secondary_donor_id", flat=True))
        ),
    }
    return hash_parts(attributes)


def cache_key(namespace, request, **extra):
    parts = {
        "query": request.query_params.dict(),
        "extra": extra,
    }
    return f"drp:{namespace}:{generation(namespace)}:{permission_scope(request)}:{hash_parts(parts)}"


def scoped_get(request, namespace, producer, extra=None, timeout=DEFAULT_TIMEOUT):
    return get_or_compute(cache_key(namespace, request, **(extra or {})), producer, timeout)


def get_source_defaults(source_id):
    if not source_id:
        return None
    from sharepoint_rest_api.models import SourceId  # noqa: PLC0415

    key = f"drp:{SOURCE_FILTERS_NAMESPACE}:{generation(SOURCE_FILTERS_NAMESPACE)}:{hash_parts(source_id)}"

    def load():
        return SourceId.objects.filter(source_id=source_id).values_list("default_filters", flat=True).first()

    return get_or_compute(key, load)


class CachedReadOnlyMixin:
    cache_namespace = REFERENCE_NAMESPACE
    cache_timeout = DEFAULT_TIMEOUT
    uncached_actions = ()

    def list(self, request, *args, **kwargs):
        if self.action in self.uncached_actions:
            return super().list(request, *args, **kwargs)
        data = scoped_get(
            request,
            self.cache_namespace,
            lambda: super(CachedReadOnlyMixin, self).list(request, *args, **kwargs).data,
            {"action": "list", "kwargs": kwargs},
            self.cache_timeout,
        )
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        if self.action in self.uncached_actions:
            return super().retrieve(request, *args, **kwargs)
        data = scoped_get(
            request,
            self.cache_namespace,
            lambda: super(CachedReadOnlyMixin, self).retrieve(request, *args, **kwargs).data,
            {"action": "retrieve", "kwargs": kwargs},
            self.cache_timeout,
        )
        return Response(data)
