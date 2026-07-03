# SharePoint Access

The portal accesses donor report data stored in SharePoint through **three mechanisms** provided by the [`sharepoint-rest-api`](https://pypi.org/project/sharepoint-rest-api/) package.

## Access Mechanisms

### 1. SharePoint REST API

Direct CRUD operations on SharePoint lists, items, files, and folders.

| Variant | Endpoint | ViewSet |
|---|---|---|
| URL-based | `/api/sharepoint/<tenant>/<site>/<folder>/rest/` | `DRPSharePointUrlRestViewSet` |
| Settings-based | `/api/sharepoint/<folder>/rest/` | `DRPSharePointSettingsRestViewSet` |

### 2. SharePoint CAML Queries

Filtered list queries using Collaborative Application Markup Language (CAML).

| Variant | Endpoint | ViewSet |
|---|---|---|
| URL-based | `/api/sharepoint/<tenant>/<site>/<folder>/caml/` | `DRPSharePointUrlCamlViewSet` |
| Settings-based | `/api/sharepoint/<folder>/caml/` | `DRPSharePointSettingsCamlViewSet` |

### 3. Search

There are **two search backends** — REST/CAML search (legacy) and Graph API search (recommended).

#### Microsoft Graph Search API (KQL)

KQL-based search using the Microsoft Graph Search API. This is the primary search mechanism for cross-library full-text search, with dynamic field mapping and per-source default filters.

- **ViewSet**: `DRPGraphBasedSearchViewSet`
- **Endpoints**: `/api/graph/search/`, `/api/sharepoint/search/`
- **Searchable properties**: limited to `Donor` by default (`SEARCHABLE_PROPERTIES`)

Source ID filtering — when a `source_id` query param is provided, the viewset loads default filters from the `SourceId` model, including:
- `filters` — key/value query params to inject
- `exclude_paths` — paths to exclude via `-Path:"..."` KQL
- `search_kql` — a KQL snippet AND-ed with the user's search

Field mapping is derived dynamically from the serializer's `_declared_fields` using `get_property_name_map()` / `get_property_name_reverse()`. Serializer fields map to SharePoint managed properties with `DRP_` or `CTN` prefixes (e.g. `DRPDonor`, `CTNContributionNumber`).

Returns paginated results with a `total_rows` count. Supports CSV export via `/api/graph/search/export`.

#### REST/CAML-based Search

Uses the SharePoint search API with REST or CAML backends.

| Variant | Endpoint | ViewSet |
|---|---|---|
| URL-based | `/api/sharepoint/<tenant>/<site>/search/` | `DRPSharePointUrlSearchViewSet` |

Supports three serializers selected via `?serializer=` query param:
- default → `DRPSharePointSearchSerializer` (DRP fields)
- `gavi` → `GaviSharePointSearchSerializer` (CTN-prefixed fields)
- `soa` → `GaviSoaSharePointSearchSerializer`

Searchable fields are prefixed with `DRP` or `CTN` and mapped via custom serializer fields (`DRPSearchSharePointField`, `CTNSearchSharePointField`, etc.). Public access is determined by source ID — thematic sources are public; internal/pool sources require a `@unicef.org` user.

### File Downloads

| Variant | Endpoint | ViewSet |
|---|---|---|
| URL-based | `/api/sharepoint/<tenant>/<site>/<folder>/files/` | `DRPSharePointUrlFileViewSet` |
| Settings-based | `/api/sharepoint/<folder>/files/` | `DRPSharePointSettingsFileViewSet` |

### SharePoint Groups

- **Endpoint**: `/api/sharepoint/groups/`
- **ViewSet**: `SharePointGroupViewSet` (read-only model viewset)

## Configuration

### Environment Variables

| Variable | Purpose |
|---|---|
| `SHAREPOINT_USERNAME` | SharePoint account username |
| `SHAREPOINT_PASSWORD` | SharePoint account password |
| `AZURE_CLIENT_ID` | Azure AD app registration client ID |
| `AZURE_CLIENT_SECRET` | Azure AD app registration client secret |
| `AZURE_TENANT` | Azure AD tenant (e.g. `unicef.org`) |

### Source IDs

Search is scoped by source IDs (configured in `config/fragments/drp.py`):

| Source | Internal | External |
|---|---|---|
| Certified Reports | `DRP_SOURCE_ID_INTERNAL` | `DRP_SOURCE_ID_EXTERNAL` |
| Pooled Funding | `DRP_SOURCE_ID_POOL_INTERNAL` | `DRP_SOURCE_ID_POOL_EXTERNAL` |
| Thematic | `DRP_SOURCE_ID_THEMATIC_INTERNAL` | `DRP_SOURCE_ID_THEMATIC_EXTERNAL` |
| Gavi | `DRP_SOURCE_ID_GAVI` | |
| Gavi SOA | `DRP_SOURCE_ID_GAVI_SOA` | |

Source IDs can also be stored in the database via the `SourceId` model (see `api/views/metadata.py`), which supports per-source default filters (JSON with `filters`, `exclude_paths`, `search_kql` keys) used by the Graph search viewset.

### Fixtures

SharePoint tenant, site, and library definitions are loaded from `src/donor_reporting_portal/apps/core/fixtures/libraries.json`:

- 1 tenant: `unicef.sharepoint.com`
- 1 site: `GLB-DRP` (type: `sites`)
- ~70 libraries (e.g. "2020 Certified Reports", "Thematic Reports", "GrantDocuments_External/Internal")

The `SharePointGroup` model groups libraries for permission and display purposes (managed via Django admin).

### Serializer Field Mapping

SharePoint list columns are mapped to DRF fields using custom field types:

| Field | Purpose |
|---|---|
| `SharePointPropertyField` | Single-value REST/CAML property |
| `SharePointPropertyManyField` | Multi-value REST/CAML property |
| `UpperSharePointPropertyField` | Uppercased property |
| `DRPSearchSharePointField` / `CTNSearchSharePointField` | Single-value Graph/REST search field (prefixes `DRP`/`CTN`) |
| `DRPSearchMultiSharePointField` / `CTNSearchMultiSharePointField` | Multi-value Graph/REST search field |

See `api/serializers/sharepoint.py` and `api/serializers/fields.py` for the full set.

## Permissions

- Authentication: **Azure AD B2C** OAuth2 via `UNICEFAzureADB2COAuth2` backend
- Access control: `DonorPermission` and `PublicLibraryPermission` mixins (combined via `|` operator)
- File endpoints: `DonorPermission` only
- Public access: thematic source IDs are publicly accessible

## Key Source Files

| File | Purpose |
|---|---|
| `api/views/sharepoint.py` | All SharePoint API viewsets (REST, CAML, Graph search, files) |
| `api/serializers/sharepoint.py` | DRP, Gavi, Gavi SOA serializers |
| `api/serializers/fields.py` | Custom search field types (`DRPSearchSharePointField`, `CTNSearchSharePointField`, etc.) |
| `api/permissions.py` | `DonorPermission` and `PublicLibraryPermission` |
| `api/urls.py` | All API route definitions |
| `apps/sharepoint/models.py` | `SharePointGroup` model |
| `apps/sharepoint/admin.py` | Django admin configuration |
| `apps/core/fixtures/libraries.json` | Initial SharePoint tenant/site/library data |
| `config/fragments/drp.py` | Source ID and DRP-specific settings |
