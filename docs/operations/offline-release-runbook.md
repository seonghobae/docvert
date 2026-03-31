# Docvert Offline Release Runbook

This document describes how to prepare and deploy Docvert in an air-gapped (폐쇄망) or strictly offline environment.

## Context

Docvert depends on several system-level libraries (e.g., `poppler-utils`, `tesseract-ocr`, `libmagic-dev`) to successfully parse PDFs and extract data. Because of this, distributing a standard Python "wheelhouse" is insufficient for a pure offline install, as the target system may lack these binaries. 

The canonical and safest method for an offline release is to build a self-contained **Docker Image**, save it as a tarball, and distribute it.

## Preparation (Online Environment)

Run the automated build script on a machine with internet access and Docker installed:

```bash
./scripts/build_offline_bundle.sh
```

**What the script does:**
1. Builds the `docvert:offline` Docker image, pulling all Python dependencies (including large ML models via `docling`) and apt packages.
2. Saves the image to a tarball (`docker save`).
3. Compresses the image and bundles it with a `README-OFFLINE.md`.
4. Produces a final `docvert-offline-release.tar.gz` archive.

## Deployment (Offline Environment)

1. Transfer `docvert-offline-release.tar.gz` to the target air-gapped machine via secure media (e.g., USB, secure file transfer).
2. Extract the archive:
   ```bash
   tar -xzvf docvert-offline-release.tar.gz
   cd docvert-offline-release
   ```
3. Load the Docker image into the local registry:
   ```bash
   docker load -i docvert-offline.tar.gz
   ```
4. Verify the image is available:
   ```bash
   docker images | grep docvert
   ```

## Execution

To use Docvert, mount the target files/directories into the container's volume. By convention, we use `/data` as the mount point.

**Convert a single file:**
```bash
docker run --rm \
    -v $(pwd):/data \
    docvert:offline convert /data/input.pdf --output-dir /data/out
```

**Convert a directory (batch):**
```bash
docker run --rm \
    -v $(pwd)/input_docs:/data/in \
    -v $(pwd)/output_docs:/data/out \
    docvert:offline batch /data/in --output-dir /data/out
```

## Maintenance & Updates

When a new version of Docvert is released, or when dependencies change:
1. Re-run `./scripts/build_offline_bundle.sh` on the internet-connected build machine.
2. Transfer the new archive to the offline environment.
3. Reload the image using `docker load`. The `latest` (or `offline`) tag will automatically point to the newly loaded image.
