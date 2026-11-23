from ..settings import env


def _source_id(name):
    """Read a source ID, ignoring stray commas/whitespace from shell env files."""
    value = env(name, default=None)
    if value is None:
        return None
    return value.strip().strip(",").strip() or None


DRP_SOURCE_IDS = {
    "internal": _source_id("DRP_SOURCE_ID_INTERNAL"),
    "external": _source_id("DRP_SOURCE_ID_EXTERNAL"),
    "pool_internal": _source_id("DRP_SOURCE_ID_POOL_INTERNAL"),
    "pool_external": _source_id("DRP_SOURCE_ID_POOL_EXTERNAL"),
    "thematic_internal": _source_id("DRP_SOURCE_ID_THEMATIC_INTERNAL"),
    "thematic_external": _source_id("DRP_SOURCE_ID_THEMATIC_EXTERNAL"),
    "gavi": _source_id("DRP_SOURCE_ID_GAVI"),
    "gavi_soa": _source_id("DRP_SOURCE_ID_GAVI_SOA"),
}

GAVI_DONOR_CODE = "I49928"
