#!/usr/bin/env bash
set -e

echo "Building offline release bundle for Docvert..."

# 1. Create a release directory
RELEASE_DIR="docvert-offline-release"
rm -rf $RELEASE_DIR
mkdir -p $RELEASE_DIR

# 2. Build the docker image
echo "Building docker image..."
docker build -t docvert:offline .

# 3. Save the docker image
echo "Saving docker image to tarball..."
docker save -o $RELEASE_DIR/docvert-offline.tar docvert:offline

# 4. Compress the image
echo "Compressing docker image..."
gzip $RELEASE_DIR/docvert-offline.tar

# 5. Create offline instruction README
cat << 'README' > $RELEASE_DIR/README-OFFLINE.md
# Docvert Offline Release

This package contains everything needed to run Docvert in an air-gapped/offline environment using Docker.

## Prerequisites
- Docker (or Podman) installed on the target machine.

## Installation

1. Load the Docker image from the tarball:
   ```bash
   docker load -i docvert-offline.tar.gz
   ```

2. Verify the image is loaded:
   ```bash
   docker images | grep docvert
   ```

## Usage

You can run Docvert by mounting your local directories into the container.

**Example: Convert a single file**
```bash
docker run --rm \
    -v $(pwd):/data \
    docvert:offline convert /data/input.pdf --output-dir /data/out
```

**Example: Batch processing**
```bash
docker run --rm \
    -v $(pwd)/my_docs:/data/my_docs \
    -v $(pwd)/out:/data/out \
    docvert:offline batch /data/my_docs --output-dir /data/out
```

*Note: Replace `docker` with `podman` if that is your container engine.*
README

# 6. Package the final release zip
echo "Creating final offline release archive..."
tar -czvf docvert-offline-release.tar.gz $RELEASE_DIR

# Clean up build dir
rm -rf $RELEASE_DIR

echo "Done! Offline release bundle is available at: docvert-offline-release.tar.gz"
