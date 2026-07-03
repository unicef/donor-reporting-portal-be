# Contributing

## Development Workflow

This project uses **git-flow** for release management.

### Branches

- `develop` — active development
- `master` — stable releases
- `feature/*` — feature branches
- `release/*` — release branches

### Making Changes

1. Create a feature branch from `develop`
2. Make your changes
3. Run tests: `pytest`
4. Run linting via pre-commit (see [Code Style](#code-style) for all hooks)
5. Open a pull request to `develop`

### Release Process

```bash
# Start a release
git flow release start <version>

# Update CHANGES and version in __init__.py
make build
make release

# Finish the release
git flow release finish <version>
```

## Code Style

Linting is handled through **pre-commit** hooks — after cloning, run `pre-commit install`.

Available hooks: `end-of-file-fixer`, `trailing-whitespace`, `check-github-workflows`, `tox-ini-fmt`, `pyproject-fmt`, `ruff-format`, `ruff`, `djade`, `check-useless-excludes`.

To run all hooks manually: `pre-commit run --all-files`
