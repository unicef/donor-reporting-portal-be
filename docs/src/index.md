# Donor Reporting Portal

The **Donor Reporting Portal (DRP)** is a Django-based backend API that provides UNICEF staff and donors with access to donor reports stored in Microsoft SharePoint.

It integrates with SharePoint through three mechanisms — **REST API**, **CAML queries**, and **Microsoft Graph Search** — and enforces access control via **Azure AD B2C** authentication.

## Repositories

- Backend: [github.com/unicef/donor-reporting-portal](https://github.com/unicef/donor-reporting-portal)
- Frontend: [github.com/unicef/donor-reporting-portal-frontend](https://github.com/unicef/donor-reporting-portal-frontend)

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python >= 3.14 |
| Framework | Django 6.0 |
| REST API | Django REST Framework 3.17 |
| SharePoint SDK | sharepoint-rest-api 0.20, Office365-REST-Python-Client 2.6 |
| Task Queue | Celery 5.6 |
| Auth | Azure AD B2C (social-auth-app-django 6.0) |
| Database | PostgreSQL (psycopg2) |
| Cache | Redis |
| Server | Gunicorn 26.0 |
| Monitoring | Sentry SDK 2.64 |
| UNICEF Libraries | unicef-security 1.10, unicef-notification 1.4, unicef-vision 0.6 |

## Quick Start

```bash
cp .env_template .env
python manage.py upgrade --all
```
