# Settings

## Environment Variables

DRP uses [django-environ](https://github.com/joke2k/django-environ) to manage configuration through environment variables.

### Core Django Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_SETTINGS_MODULE` | Python path to settings module | `donor_reporting_portal.config.settings` | Yes |
| `SECRET_KEY` | Django secret key for cryptographic signing | - | Yes |
| `DEBUG` | Enable debug mode (never use in production) | `False` | No |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames | `*` | No |
| `SESSION_COOKIE_SECURE` | Secure flag on session cookies | `True` | No |

### Database

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string (format: `psql://user:pass@host:port/dbname`) | - | Yes |

### Redis / Cache

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDIS_URL` | Redis connection string (format: `redis://host:port/db`) | - | Yes |

### Azure AD

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AZURE_CLIENT_ID` | Azure AD app registration client ID | - | Yes |
| `AZURE_CLIENT_SECRET` | Azure AD app registration client secret | - | Yes |
| `AZURE_TENANT` | Azure AD tenant domain | `unicef.org` | Yes |

### Azure AD B2C (Authentication)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AZURE_B2C_CLIENT_ID` | Azure AD B2C application client ID | - | Yes |
| `AZURE_B2C_CLIENT_SECRET` | Azure AD B2C application client secret | - | Yes |
| `AZURE_B2C_TENANT` | Azure AD B2C tenant name | - | Yes |

### SharePoint

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SHAREPOINT_USERNAME` | SharePoint service account username | - | Yes |
| `SHAREPOINT_PASSWORD` | SharePoint service account password | - | Yes |

### UNICEF Insight

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `INSIGHT_URL` | UNICEF Insight API base URL | `https://uniapis.azure-api.net/biapi/v1/` | Yes |
| `INSIGHT_SUB_KEY` | UNICEF Insight API subscription key | - | Yes |

### Celery

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CELERY_TASK_ALWAYS_EAGER` | Execute tasks synchronously (for development) | `True` | No |
| `CELERY_BROKER_URL` | Celery broker URL (defaults to `REDIS_URL`) | - | No |

### DRP Source IDs

These configure the SharePoint search source IDs for different report categories:

| Variable | Description | Default |
|----------|-------------|---------|
| `DRP_SOURCE_ID_INTERNAL` | Internal Certified Reports source ID | `None` |
| `DRP_SOURCE_ID_EXTERNAL` | External Certified Reports source ID | `None` |
| `DRP_SOURCE_ID_POOL_INTERNAL` | Internal Pooled Funding source ID | `None` |
| `DRP_SOURCE_ID_POOL_EXTERNAL` | External Pooled Funding source ID | `None` |
| `DRP_SOURCE_ID_THEMATIC_INTERNAL` | Internal Thematic Reports source ID | `None` |
| `DRP_SOURCE_ID_THEMATIC_EXTERNAL` | External Thematic Reports source ID | `None` |
| `DRP_SOURCE_ID_GAVI` | Gavi source ID | `None` |
| `DRP_SOURCE_ID_GAVI_SOA` | Gavi SOA source ID | `None` |

### Email (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_HOST` | SMTP server hostname | - |
| `EMAIL_PORT` | SMTP server port | `587` |
| `EMAIL_HOST_USER` | SMTP username | - |
| `EMAIL_HOST_PASSWORD` | SMTP password | - |
| `EMAIL_USE_TLS` | Enable TLS for email | `True` |

### Sentry (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `SENTRY_DSN` | Sentry Data Source Name for error tracking | - |
| `SENTRY_TRACES_SAMPLE_RATE` | Percentage of transactions to sample (0.0-1.0) | `0.1` |

### CORS (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ALLOWED_ORIGINS` | Comma-separated list of allowed origins | - |

## Settings Fragments

DRP uses modular settings files in `config/fragments/`:

| File | Purpose |
|------|---------|
| `drp.py` | DRP-specific settings and source IDs |
| `insight.py` | UNICEF Insight API configuration |
| `celery.py` | Celery task queue configuration |
| `cache.py` | Redis cache configuration |
| `social_auth.py` | Azure AD B2C social auth settings |
| `rest.py` | Django REST Framework settings |
| `jwt.py` | JWT token configuration |
| `mail.py` | Email backend settings |
| `sentry.py` | Sentry error tracking settings |
| `cors.py` | CORS configuration |
| `log.py` | Logging configuration |
| `matomo.py` | Matomo analytics settings |
| `impersonate.py` | User impersonation settings |

## Checking Your Configuration

Use the management command to verify your environment is correctly configured:

```bash
python manage.py env --check
```

This will validate that all required environment variables are set.
