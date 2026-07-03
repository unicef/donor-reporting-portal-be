# Process

## Overview

Donors and UNICEF staff use the Donor Reporting Portal to access donor reports and documents stored in Microsoft SharePoint.

## Authentication & Access

1. User visits the portal and authenticates via **Azure AD B2C** (OAuth2)
2. A JWT token is issued and sent with each API request
3. DRP validates the token and resolves the user's role (donor or UNICEF staff)
4. `DonorPermission` / `PublicLibraryPermission` guards enforce access to specific SharePoint libraries

## Searching Documents

Users search for documents through the portal's search interface:

- **Microsoft Graph Search API (KQL)** — primary search mechanism for cross-library full-text search
- **REST/CAML-based Search** — legacy search using SharePoint search API

Search is scoped by **source ID** (Certified Reports, Pooled Funding, Thematic, Gavi, etc.) and filtered by donor permissions.

### Search Flow

1. User submits a search query through the frontend
2. Request hits the Graph search viewset (`/api/graph/search/`) or REST/CAML search viewset
3. Source ID filtering applies default filters, exclusion paths, and KQL snippets
4. SharePoint managed properties (prefixed `DRP_` or `CTN_`) are mapped to serializer fields
5. Results are returned paginated with a `total_rows` count
6. Results can be exported as CSV (`/api/graph/search/export`)

## Browsing SharePoint Libraries

Users browse documents organised by SharePoint libraries:

- **URL-based access** — dynamic tenant/site resolution via `/api/sharepoint/<tenant>/<site>/<folder>/`
- **Settings-based access** — config-driven resolution via `/api/sharepoint/<folder>/`

Supported operations:
- List items in a folder (REST API or CAML queries)
- Read file contents
- Download files

## Downloading Documents

Files are downloaded through file endpoints:

1. User requests a file via `/api/sharepoint/<folder>/files/` or `/api/sharepoint/<tenant>/<site>/<folder>/files/`
2. DRP authenticates to SharePoint and streams the file
3. `DonorPermission` enforces access control

## Metadata Synchronisation

Donor, Grant, External Grant, and Theme metadata are synchronised from the **dsgrants** service in UNICEF Insight via `GrantSynchronizer`:

1. Periodic sync pulls metadata from UNICEF Insight
2. Data is stored in local models (`Donor`, `Grant`, `ExternalGrant`, `Theme`)
3. Metadata is used to filter and organise SharePoint documents

## SharePoint Configuration

SharePoint tenant, site, and library definitions are loaded from fixtures:
- 1 tenant: `unicef.sharepoint.com`
- 1 site: `GLB-DRP`
- ~70 libraries grouped by `SharePointGroup` for permission and display purposes
