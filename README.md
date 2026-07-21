# Donor Reporting Portal Backend

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![Django 6.0](https://img.shields.io/badge/django-6.0-green.svg)](https://www.djangoproject.com/)

The **Donor Reporting Portal (DRP)** is a Django-based backend API that provides UNICEF staff and donors with access to donor reports stored in Microsoft SharePoint.

## Overview

DRP integrates with SharePoint through three mechanisms:
- **REST API** — Direct CRUD operations on lists, items, files, and folders
- **CAML Queries** — Filtered list queries using Collaborative Application Markup Language
- **Microsoft Graph Search** — KQL-based cross-library full-text search

Access control is enforced via **Azure AD B2C** authentication with role-based permissions for donors and UNICEF staff.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python >= 3.14 |
| Framework | Django 6.0 |
| REST API | Django REST Framework 3.17 |
| SharePoint | sharepoint-rest-api 0.20, Office365-REST-Python-Client 2.6 |
| Task Queue | Celery 5.6 |
| Auth | Azure AD B2C (social-auth-app-django 6.0) |
| Database | PostgreSQL |
| Cache | Redis |
| Server | Gunicorn 26.0 |
| Monitoring | Sentry SDK 2.64 |

## Quick Start

### Prerequisites

- Python 3.14+
- PostgreSQL
- Redis

### Installation

```bash
# Clone the repository
git clone https://github.com/unicef/donor-reporting-portal.git
cd donor-reporting-portal

# Create virtual environment and install dependencies
uv venv .venv --python 3.14
source .venv/bin/activate
uv sync

# Install pre-commit hooks
pre-commit install

# Configure environment
cp .env_template .env
# Edit .env with your credentials

# Run database migrations and load fixtures
python manage.py upgrade --all

# Start development server
python manage.py runserver
```

### Docker

```bash
cd docker
make build run
```

Or using docker compose:

```bash
docker compose up
```

Navigate to http://localhost:8000/admin/ and login using `admin@example.com/password`

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `SECRET_KEY` | Django secret key | Yes |
| `AZURE_CLIENT_ID` | Azure AD app registration client ID | Yes |
| `AZURE_CLIENT_SECRET` | Azure AD app registration client secret | Yes |
| `AZURE_TENANT` | Azure AD tenant (e.g., `unicef.org`) | Yes |
| `AZURE_B2C_CLIENT_ID` | Azure AD B2C client ID | Yes |
| `AZURE_B2C_CLIENT_SECRET` | Azure AD B2C client secret | Yes |
| `AZURE_B2C_TENANT` | Azure AD B2C tenant | Yes |
| `SHAREPOINT_USERNAME` | SharePoint account username | Yes |
| `SHAREPOINT_PASSWORD` | SharePoint account password | Yes |
| `INSIGHT_URL` | UNICEF Insight API URL | Yes |
| `INSIGHT_SUB_KEY` | UNICEF Insight subscription key | Yes |
| `DEBUG` | Enable debug mode | No |
| `CELERY_TASK_ALWAYS_EAGER` | Run Celery tasks synchronously | No |

See [docs/src/settings.md](docs/src/settings.md) for complete configuration details.

## Development

### Testing

```bash
pytest
```

Tests use **VCR.py** cassettes for recording SharePoint HTTP interactions.

### Code Quality

- Linting: `ruff` (config in `ruff.toml`)
- Pre-commit hooks: `pre-commit install`
- Run all hooks: `pre-commit run --all-files`

### Documentation

Full documentation is available in the [docs/](docs/src/index.md) directory (served via MkDocs):

```bash
# Install docs dependencies
uv sync --group docs

# Serve documentation locally
mkdocs serve
```

## Project Structure

```
src/donor_reporting_portal/
├── api/                  # REST API layer
│   ├── views/            # DRF viewsets
│   ├── serializers/      # Request/response serializers
│   ├── permissions.py    # Permission classes
│   └── urls.py           # API route definitions
├── apps/                 # Django apps
│   ├── core/             # Core app (backends, fixtures, management commands)
│   ├── report_metadata/  # Donor/grant metadata + Insight synchronisers
│   ├── roles/            # User roles & permissions
│   └── sharepoint/       # SharePoint integration (models, admin)
├── config/               # Django settings
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── fragments/        # Modular settings (drp.py, insight.py, ...)
└── libs/                 # Shared utilities
```

## Deployment

Deployment is performed through **Azure Pipelines** with continuous delivery:

1. Push to `develop` or `master` triggers a pipeline
2. A Docker image is built and uploaded to **Azure Container Registry**
3. Test and production environments are updated automatically

## Troubleshooting

- Exceptions are logged in Sentry: https://sentry.io/unicef-jk/
- Each container in Rancher allows access to local logs

## Contributing

See [docs/src/contributing.md](docs/src/contributing.md) for development workflow and code style guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
