# Setup


### System Requirements

- [python](https://www.python.org/)
- [direnv](https://direnv.net/) - not mandatory but strongly recommended
- [uv](https://docs.astral.sh/uv/)
- [postgres](https://www.postgresql.org/)
- [redis](https://redis.io/)

### 1. Clone repo and install requirements
    git clone https://github.com/unicef/donor-reporting-portal
    uv venv .venv --python 3.14
    source .venv/bin/activate
    uv sync
    pre-commit install

### 2. configure your environment

Uses `./manage.py env` to check required (and optional) variables to put

    ./manage.py env --check


### 3. Run upgrade to run migrations and initial setup

    ./manage.py upgrade
