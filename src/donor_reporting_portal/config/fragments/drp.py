from ..settings import env

DRP_SOURCE_IDS = {
    "internal": env("DRP_SOURCE_ID_INTERNAL", default=None),
    "external": env("DRP_SOURCE_ID_EXTERNAL", default=None),
    "pool_internal": env("DRP_SOURCE_ID_POOL_INTERNAL", default=None),
    "pool_external": env("DRP_SOURCE_ID_POOL_EXTERNAL", default=None),
    "thematic_internal": env("DRP_SOURCE_ID_THEMATIC_INTERNAL", default=None),
    "thematic_external": env("DRP_SOURCE_ID_THEMATIC_EXTERNAL", default=None),
    "gavi": env("DRP_SOURCE_ID_GAVI", default=None),
    "gavi_soa": env("DRP_SOURCE_ID_GAVI_SOA", default=None),
}

GAVI_DONOR_CODE = "I49928"
