# Installation Guide (Zero-Setup, Per-OS)

DocVert is a Python-based CLI tool that converts complex PDF and DOCX documents into clean, semantic Markdown. This guide assumes **you have nothing installed** — no Homebrew, no package manager, no Python.

---

## Table of Contents

- [Docker Installation (All OS — Recommended)](#docker-installation-all-os-recommended)
- [Air-Gapped / Offline Installation](#air-gapped-offline-installation)
- [macOS Native Installation (No Homebrew)](#macos-native-installation-no-homebrew)
- [Windows Installation](#windows-installation)
- [Linux (Ubuntu/Debian) Installation](#linux-ubuntudebian-installation)
- [Linux (RHEL/CentOS/Fedora) Installation](#linux-rhelcentosfedora-installation)
- [Troubleshooting](#troubleshooting)

---

## Docker Installation (All OS — Recommended)

DocVert depends on complex system libraries (poppler, tesseract, etc.) and AI models internally. Using the **pre-built Docker image is the easiest and safest** approach on any OS.

### Step 1: Install Docker

Download and install Docker using the GUI installer for your OS. **No Homebrew or package manager required.**

| OS | How to Install |
|---|---|
| **macOS** | Download `.dmg` from [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/) → double-click → drag to Applications → launch Docker Desktop |
| **Windows** | Download `.exe` from [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) → run installer → reboot → launch Docker Desktop |
| **Linux** | See commands below |

**Linux Docker installation (apt):**
```bash
# Add Docker's official GPG key
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Allow current user to run Docker (re-login required)
sudo usermod -aG docker $USER
```

### Step 2: Get the DocVert Docker Image

**Option A — Download from GitHub Releases (online):**

Go to the [DocVert Releases page](https://github.com/seonghobae/docvert/releases), download all `.part-*` files from the latest release, then:

```bash
# Combine split files
cat docvert-offline-release.tar.gz.part-* > docvert-offline-release.tar.gz

# Extract
tar -xzvf docvert-offline-release.tar.gz
cd docvert-offline-release

# Load Docker image
docker load -i docvert-offline.tar.gz

# Verify
docker images | grep docvert
```

**Option B — Build from source:**

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
docker build -t docvert:offline .
```

### Step 3: Run Conversions

```bash
# Convert a single file
docker run --rm \
    -v $(pwd):/data \
    docvert:offline convert /data/input.pdf --output-dir /data/out

# Batch convert a directory
docker run --rm \
    -v $(pwd)/my_docs:/data/my_docs \
    -v $(pwd)/out:/data/out \
    docvert:offline batch /data/my_docs --output-dir /data/out
```

> **Windows PowerShell:** Use `${PWD}` instead of `$(pwd)`.
>
> **Windows CMD:** Use `%cd%` instead of `$(pwd)`.

---

## Air-Gapped / Offline Installation

For environments with no internet access (secure networks, classified systems).

### Preparation (on a machine with internet)

1. Go to [DocVert GitHub Releases](https://github.com/seonghobae/docvert/releases) and download all `.part-*` files from the latest release.
2. Transfer the files to the air-gapped machine via USB, CD, or secure file transfer.

### Installation (on the air-gapped machine)

**Prerequisite:** Docker (or Podman) must be installed on the target machine.

```bash
# 1. Combine split files
cat docvert-offline-release.tar.gz.part-* > docvert-offline-release.tar.gz

# 2. Extract
tar -xzvf docvert-offline-release.tar.gz
cd docvert-offline-release

# 3. Load the Docker image
docker load -i docvert-offline.tar.gz

# 4. Verify
docker images | grep docvert
```

### Usage

```bash
# Single file
docker run --rm -v $(pwd):/data \
    docvert:offline convert /data/document.pdf --output-dir /data/out

# Batch
docker run --rm \
    -v $(pwd)/input:/data/input \
    -v $(pwd)/output:/data/output \
    docvert:offline batch /data/input --output-dir /data/output
```

> **Tip:** Replace `docker` with `podman` if your environment uses Podman.

### Updating

Download new `.part-*` files from the Releases page, repeat the same process. The existing image will be replaced automatically.

---

## macOS Native Installation (No Homebrew)

This guide installs DocVert directly on macOS **without Homebrew**. Open Terminal.app and follow each step.

### Step 1: Install Command Line Tools

```bash
xcode-select --install
```

Click **"Install"** in the popup and wait for completion. Skip if already installed.

### Step 2: Install System Libraries via MacPorts

Instead of Homebrew, we use [MacPorts](https://www.macports.org/install.php).

**Install MacPorts:**

1. Go to the [MacPorts download page](https://www.macports.org/install.php) and download the `.pkg` installer for your macOS version.
2. Double-click the `.pkg` file to install.
3. Close and reopen Terminal so the PATH takes effect.

**Install required libraries:**

```bash
sudo port install poppler tesseract libmagic
```

### Step 3: Install the `uv` Package Manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Close and reopen Terminal after installation.

### Step 4: Download and Install DocVert

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

### Step 5: Verify Installation

```bash
uv run python -m docvert.cli.main --help
```

> **Alternative: Conda**
>
> You can use [Miniconda](https://docs.anaconda.com/miniconda/install/) instead of MacPorts:
>
> ```bash
> # Download and install Miniconda (.pkg from web, or via CLI)
> curl -fsSL https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -o miniconda.sh
> bash miniconda.sh -b -p $HOME/miniconda
> eval "$($HOME/miniconda/bin/conda shell.bash hook)"
>
> # Install system libraries
> conda install -c conda-forge poppler tesseract libmagic
>
> # Then install uv and DocVert as above
> ```

---

## Windows Installation

On Windows, we strongly recommend **WSL2 (Windows Subsystem for Linux)** due to system library compatibility.

### Step 1: Install WSL2 and Ubuntu

Open **PowerShell** or **Command Prompt** as **Administrator**:

```cmd
wsl --install
```

**Reboot** your computer. After reboot, an Ubuntu window will open — set your username and password.

> **Note:** Requires Windows 10 version 2004+ or Windows 11. For older versions, see the [manual WSL installation guide](https://learn.microsoft.com/en-us/windows/wsl/install-manual).

### Step 2: Install System Libraries

In the Ubuntu (WSL) terminal:

```bash
sudo apt update
sudo apt install -y poppler-utils tesseract-ocr libmagic-dev curl git
```

### Step 3: Install `uv` Package Manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Run the following or restart the terminal:

```bash
source $HOME/.local/bin/env
```

### Step 4: Download and Install DocVert

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

### Step 5: Verify Installation

```bash
uv run python -m docvert.cli.main --help
```

### Accessing Windows Files from WSL

Use the `/mnt/c/` path to access Windows files:

```bash
# Example: convert a file from Desktop
uv run python -m docvert.cli.main convert \
    "/mnt/c/Users/YourUsername/Desktop/document.pdf" \
    --output-dir ./results
```

---

## Linux (Ubuntu/Debian) Installation

### Step 1: Install System Libraries

```bash
sudo apt update
sudo apt install -y poppler-utils tesseract-ocr libmagic-dev curl git
```

### Step 2: Install `uv` Package Manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your terminal after installation.

### Step 3: Download and Install DocVert

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

### Step 4: Verify Installation

```bash
uv run python -m docvert.cli.main --help
```

---

## Linux (RHEL/CentOS/Fedora) Installation

### Step 1: Install System Libraries

**Fedora:**
```bash
sudo dnf install -y poppler-utils tesseract libmagic curl git
```

**RHEL / CentOS / Rocky Linux / AlmaLinux:**
```bash
sudo dnf install -y epel-release
sudo dnf install -y poppler-utils tesseract libmagic curl git
```

### Step 2: Install `uv` Package Manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your terminal.

### Step 3: Download and Install DocVert

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

### Step 4: Verify Installation

```bash
uv run python -m docvert.cli.main --help
```

---

## Troubleshooting

### `poppler` errors

```
pdfinfo not found. Install poppler-utils.
```

- **macOS (MacPorts):** `sudo port install poppler`
- **macOS (Conda):** `conda install -c conda-forge poppler`
- **Ubuntu/Debian:** `sudo apt install -y poppler-utils`
- **Fedora:** `sudo dnf install -y poppler-utils`
- **Docker:** Already included in the Docker image.

### `tesseract` errors

```
tesseract is not installed or not in PATH
```

- **macOS (MacPorts):** `sudo port install tesseract`
- **macOS (Conda):** `conda install -c conda-forge tesseract`
- **Ubuntu/Debian:** `sudo apt install -y tesseract-ocr`
- **Fedora:** `sudo dnf install -y tesseract`

### Python version issues

DocVert requires Python 3.14+. The `uv` package manager automatically handles Python version management.

```bash
# Check available Python versions
uv python list
```

### WSL2 issues (Windows)

If WSL fails to install, ensure the following Windows features are enabled:

```cmd
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

Reboot and try `wsl --install` again.
