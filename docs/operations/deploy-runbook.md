# Deploy Runbook

## Overview

DocVert is packaged as a Python CLI tool. It can be:

- Installed locally via `uv sync` (requires system libraries: poppler, tesseract, libmagic)
- Run inside a Docker container for isolated execution
- Deployed to air-gapped environments via offline Docker images from GitHub Releases

## Local Installation

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
uv run python -m docvert.cli.main --help
```

For detailed per-OS installation instructions, see the [Installation Guide](https://seonghobae.github.io/docvert/installation-guide/).

## Docker Execution

A `Dockerfile` is provided in the repository root. Build and run locally:

```bash
# Build the image
docker build -t docvert:offline .

# Convert a single file
docker run --rm -v $(pwd):/data \
    docvert:offline convert /data/input.pdf --output-dir /data/out

# Batch convert a directory
docker run --rm \
    -v $(pwd)/docs:/data/docs \
    -v $(pwd)/out:/data/out \
    docvert:offline batch /data/docs --output-dir /data/out
```

To push to a container registry:

```bash
docker build -t ghcr.io/seonghobae/docvert:latest .
docker push ghcr.io/seonghobae/docvert:latest
```

## Offline / Air-Gapped Deployment

For air-gapped environments, use the pre-built Docker images from [GitHub Releases](https://github.com/seonghobae/docvert/releases).

See the [Offline Release Runbook](offline-release-runbook.md) for detailed instructions.

## CI/CD

- **CI workflow** (`.github/workflows/ci.yml`): Runs on every PR and push to master.
  - Code quality: Ruff lint/format, Mypy type check, Interrogate docstring check
  - Tests: pytest with 100% coverage enforcement
- **Pages workflow** (`.github/workflows/pages.yml`): Deploys documentation to GitHub Pages on push to master.
- **Release workflow** (`.github/workflows/release.yml`): Triggered by Git tags (`v*`). Builds Docker offline bundle and creates GitHub Release with split archive files.

## Creating a Release

1. Update the version in `pyproject.toml`
2. Commit and merge to master
3. Create and push a Git tag:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
4. The release workflow will automatically build the Docker image, create split archives, and publish a GitHub Release.
