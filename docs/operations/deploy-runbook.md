# Deploy Runbook

## Overview
Docvert is packaged as a Python CLI tool. It can be installed locally via `uv` or `pip`, or run inside a Docker container for isolated execution (especially useful for bulk processing).

## PyPI Release
Currently, Docvert is distributed from source. A standard `pyproject.toml` is provided.
To build and publish:
```bash
uv build
uv publish
```

## Docker Execution (Optional)
If a `Dockerfile` is present in the future, the image can be built and pushed to GitHub Container Registry (GHCR):
```bash
docker build -t ghcr.io/seonghobae/docvert:latest .
docker push ghcr.io/seonghobae/docvert:latest
```

## CI/CD 
- PRs automatically trigger the `CI` workflow (testing and linting).
- Release workflows (if any) are triggered on Git tags (e.g., `v1.0.0`).
