# Docker

## Prerequisites

Before building Docker images, ensure you have:
- Docker installed
- Docker Compose (optional, for compose-based workflow)
- Redis and PostgreSQL running (either locally or via Docker)

## Quick Start with Docker Compose

The simplest way to run DRP locally is with Docker Compose:

```bash
cd docker
docker compose up
```

This will start DRP with all required services. Navigate to http://localhost:8000/admin/ and login using:
- **Username:** `admin@example.com`
- **Password:** `password`

## Building Images

### Build Base Image

The base image includes system dependencies and Python packages:

```bash
cd docker
make build-base
```

### Build Application Image

```bash
cd docker
make build
```

This builds the production image and runs deployment checks.

### Build for Development

```bash
cd docker
make build-test
```

## Running Containers

### Run Production Container

```bash
cd docker
make run
```

This starts the DRP application on port 8000.

### Run with Custom Environment Variables

```bash
export DATABASE_URL=postgres://postgres:password@127.0.0.1:5432/donor_reporting_portal
export REDIS_URL=redis://127.0.0.1:6379/1
export SECRET_KEY=your-secret-key
export AZURE_CLIENT_ID=your-client-id
export AZURE_CLIENT_SECRET=your-client-secret
export AZURE_TENANT=unicef.org
export SHAREPOINT_USERNAME=your-sharepoint-username
export SHAREPOINT_PASSWORD=your-sharepoint-password

cd docker
make run
```

### Run Celery Workers

```bash
cd docker
make workers
```

### Run Celery Beat (Scheduler)

```bash
cd docker
make beat
```

### Run All Services

```bash
cd docker
make stack
```

## Available Make Targets

| Target | Description |
|--------|-------------|
| `make build-base` | Build base image with dependencies |
| `make build` | Build production image |
| `make build-test` | Build development/test image |
| `make run` | Run application on port 8000 |
| `make workers` | Run Celery worker processes |
| `make beat` | Run Celery beat scheduler |
| `make stack` | Run all services together |
| `make release` | Push image to Docker Hub |
| `make local` | Run container with local code mounted |
| `make shell` | Open interactive shell in container |
| `make test` | Run deployment checks |
| `make info` | Show Docker images and containers |

## Container Services

The Docker image provides the following services (configured via `SERVICES` environment variable):

- `donor_reporting_portal` — Main Django application
- `celery workers` — Background task processing
- `celery beat` — Periodic task scheduling
- `flower` — Celery monitoring (optional)

**Note:** If `SERVICES` is empty, the internal `supervisord` daemon does not start.

### Example: Running Multiple Services

```bash
docker run \
    -e DATABASE_URL=postgres://... \
    -e REDIS_URL=redis://... \
    -e SERVICES="redis,workers,beat,donor_reporting_portal,flower" \
    unicef/donor-reporting-portal-backend:3.0.0
```

## Development Mode

For development with live code reloading:

```bash
cd docker
make local
```

This mounts your local code directory into the container and opens a bash shell.

## Environment Variables

Key environment variables for Docker deployment:

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `SECRET_KEY` | Django secret key | Yes |
| `AZURE_CLIENT_ID` | Azure AD client ID | Yes |
| `AZURE_CLIENT_SECRET` | Azure AD client secret | Yes |
| `AZURE_TENANT` | Azure AD tenant | Yes |
| `SHAREPOINT_USERNAME` | SharePoint username | Yes |
| `SHAREPOINT_PASSWORD` | SharePoint password | Yes |
| `DEBUG` | Enable debug mode | No |
| `SERVICES` | Comma-separated list of services to run | No |

See [Settings](settings.md) for complete environment variable documentation.

## Troubleshooting

### View Container Logs

```bash
docker logs <container_id>
```

### Access Container Shell

```bash
cd docker
make shell
```

### Run Deployment Checks

```bash
cd docker
make test
```

This runs Django's deployment checklist to verify security settings.

## Production Deployment

Production deployment is handled through **Azure Pipelines**:

1. Push to `develop` or `master` triggers the pipeline
2. Docker image is built and pushed to Azure Container Registry
3. Environments are updated automatically via continuous delivery

For manual production deployment:

```bash
cd docker
make release
```

This pushes the image to Docker Hub (requires `DOCKER_USER` and `DOCKER_PASS` environment variables).
