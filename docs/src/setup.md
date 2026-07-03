# Setup

## Prerequisites

- Python >= 3.14
- PostgreSQL
- Redis

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/unicef/donor-reporting-portal.git
cd donor-reporting-portal
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

3. Configure environment:

```bash
cp .env_template .env
```

Edit `.env` with your credentials (see [SharePoint Access](sharepoint.md#configuration) for required variables).

4. Run database migrations and load fixtures:

```bash
python manage.py upgrade --all
```

5. Start the development server:

```bash
python manage.py runserver
```

## Docker

See [docker/README.md](../docker/README.md) for Docker build and deployment instructions.

## Testing

Test are run with **pytest** and related plugins. HTTP interactions against SharePoint are recorded using **VCR.py** cassettes (stored under `tests/api/vcr_cassettes/`).

```bash
pytest
```

### CI

CI is performed through **GitHub Actions** (`.github/` workflows).

## Deployment

Deployment is performed through **Azure Pipelines** with continuous delivery:

1. Push to `develop` or `master` triggers a pipeline
2. A Docker image is built and uploaded to **Azure Container Registry**
3. With continuous delivery, test and production environments are updated automatically

## Code Quality

- Linting: `ruff` (config in `ruff.toml`)
- Pre-commit hooks: `pre-commit install`
