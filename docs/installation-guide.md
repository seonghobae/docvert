# DocVert User Guide

> DocVert converts PDF and Word (DOCX) files into clean Markdown (.md) files.
> This guide is written for **complete beginners** — no prior setup required.

---

## Which installation method should I use?

| Your situation | Recommended method | Difficulty |
|---|---|---|
| I use a Mac | [Method A: Install on macOS](#method-a-install-on-macos) | Easy |
| I use Windows | [Method B: Install on Windows](#method-b-install-on-windows) | Medium |
| I use Linux | [Method C: Install on Linux](#method-c-install-on-linux) | Easy |
| No internet (air-gapped) | [Method D: Offline Installation](#method-d-offline-air-gapped-installation) | Medium |
| I already have Docker | [Method E: Docker Installation](#method-e-docker-installation-for-docker-users) | Easy |

> **Note about Docker Desktop:** Docker Desktop uses **2-4GB+ of RAM** in the background at all times.
> If you don't already use Docker, we recommend the **native installation methods** (A, B, or C) instead.

---

## Method A: Install on macOS

### A-1. Open Terminal

1. Press `Cmd + Space` to open **Spotlight Search**.
2. Type `Terminal` and press Enter.

> Terminal is a program where you type text commands. You'll paste all commands below into this window using `Cmd + V`.

### A-2. Install Command Line Tools

Paste this into Terminal and press Enter:

```bash
xcode-select --install
```

Click **"Install"** in the popup. Wait for it to finish (5-10 minutes).

> If you see "already installed", that's fine — skip to the next step.

### A-3. Install Homebrew (Recommended)

Homebrew makes it easy to install programs on Mac.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, follow the **"Next steps"** shown at the bottom of the output. Usually something like:

```bash
echo >> ~/.zprofile
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

> **Verify:** Type `brew --version` — if you see a version number, it worked.

### A-3 Alternative: Install without Homebrew (MacPorts)

If you prefer not to use Homebrew, install [MacPorts](https://www.macports.org/install.php):

1. Download the `.pkg` installer for your macOS version.
2. Double-click to install.
3. Close and reopen Terminal.

### A-4. Install Required Programs

**If you installed Homebrew:**
```bash
brew install poppler tesseract libmagic
```

**If you installed MacPorts:**
```bash
sudo port install poppler tesseract libmagic
```

> These programs extract text from PDFs and perform OCR (text recognition on images).

### A-5. Install uv (Package Manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Close Terminal completely and reopen it** (required!).

> `uv` automatically manages the Python environment for DocVert.
> You do NOT need to install Python separately — `uv` handles it.

### A-6. Download DocVert

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

> `git clone` downloads DocVert from the internet.
> `uv sync` installs all required libraries (may take a few minutes the first time).

### A-7. Verify Installation

```bash
uv run python -m docvert.cli.main --help
```

If you see a list of commands, installation is complete! Go to [How to Use DocVert](#how-to-use-docvert).

---

## Method B: Install on Windows

Windows uses **WSL2 (Windows Subsystem for Linux)** to create a Linux environment.

### B-1. Install WSL2

1. Click **Start Menu** and search for `PowerShell`.
2. Click **"Run as Administrator"**.
3. Paste this command and press Enter:

```cmd
wsl --install
```

4. **Restart your computer** when prompted.
5. After restart, an Ubuntu window opens automatically.
6. Set a **username** and **password** (the password won't show as you type — this is normal).

> Requires **Windows 10 version 2004+** or **Windows 11**.
> Check: Start → Settings → System → About → Windows specifications

### B-2. Install Required Programs

In the Ubuntu terminal, run each command one at a time:

```bash
sudo apt update
```

Enter the password you set in B-1 when asked.

```bash
sudo apt install -y poppler-utils tesseract-ocr libmagic-dev curl git
```

### B-3. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### B-4. Download DocVert

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

### B-5. Verify Installation

```bash
uv run python -m docvert.cli.main --help
```

### B-6. Converting Windows Files

To access files on your Windows desktop from WSL:

```bash
uv run python -m docvert.cli.main convert \
    "/mnt/c/Users/YourName/Desktop/report.pdf" \
    --output-dir ./results
```

> Replace `YourName` with your actual Windows username.
> Find it by opening File Explorer and looking at `C:\Users\`.

---

## Method C: Install on Linux

### Ubuntu / Debian

```bash
# 1. Install required programs
sudo apt update
sudo apt install -y poppler-utils tesseract-ocr libmagic-dev curl git

# 2. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# 3. Download and install DocVert
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync

# 4. Verify
uv run python -m docvert.cli.main --help
```

### Fedora / RHEL / CentOS / Rocky Linux

```bash
# 1. Install required programs
sudo dnf install -y poppler-utils tesseract libmagic curl git

# 2. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# 3. Download and install DocVert
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync

# 4. Verify
uv run python -m docvert.cli.main --help
```

---

## Method D: Offline (Air-Gapped) Installation

For secure networks with no internet access. Requires Docker or Podman.

### What you need

- One computer WITH internet access
- A USB drive or secure file transfer method
- Docker or Podman installed on the air-gapped machine

### On the internet-connected computer

1. Go to [DocVert GitHub Releases](https://github.com/seonghobae/docvert/releases).
2. Download ALL `.part-*` files from the latest release.
3. Transfer them to the air-gapped machine via USB.

### On the air-gapped machine

```bash
# Navigate to the folder with downloaded files
cd /path/to/downloaded/files

# Combine the split files
cat docvert-offline-release.tar.gz.part-* > docvert-offline-release.tar.gz

# Extract
tar -xzvf docvert-offline-release.tar.gz
cd docvert-offline-release

# Load into Docker
docker load -i docvert-offline.tar.gz

# Verify
docker images | grep docvert
```

> If you see `docvert   offline`, the installation succeeded.

See [Using with Docker](#using-with-docker) for how to run it.

---

## Method E: Docker Installation (for Docker users)

> **Warning:** Docker Desktop uses **2-4GB+ of RAM** in the background.
> Only use this method if you already have Docker installed.

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
docker build -t docvert:offline .
```

---

## How to Use DocVert

### Convert a single PDF file

```bash
uv run python -m docvert.cli.main convert ./myfile.pdf --output-dir ./results
```

> **What each part means:**
>
> - `convert` — the command to convert a file
> - `./myfile.pdf` — path to the file you want to convert
> - `--output-dir ./results` — folder where results will be saved (created automatically)

### Convert a Word (DOCX) file

```bash
uv run python -m docvert.cli.main convert ./report.docx --output-dir ./results
```

### Convert all files in a folder

```bash
uv run python -m docvert.cli.main batch ./my_documents --output-dir ./results
```

> `batch` automatically finds and converts all PDF and DOCX files in the folder.

### What you get after conversion

Each file produces 3 outputs:

| File | Description |
|---|---|
| `filename.md` | The converted Markdown file (open with any text editor) |
| `filename.conversion.json` | Conversion metadata (parser used, warnings, etc.) |
| `filename.assets/` | Folder containing extracted images |

### Using with Docker

If you installed via Docker:

```bash
# Convert a file in the current folder
docker run --rm -v "$(pwd)":/data docvert:offline convert /data/myfile.pdf --output-dir /data/results

# Convert all files in a folder
docker run --rm -v "$(pwd)":/data docvert:offline batch /data/documents --output-dir /data/results
```

> **Windows PowerShell:** Use `${PWD}` instead of `$(pwd)`.

---

## Advanced: AI-Powered Refinement (Optional)

Use AI to polish the conversion results. Requires an API key.

### Using OpenAI

```bash
# Set your API key (get one at https://platform.openai.com/api-keys)
export OPENAI_API_KEY="sk-paste-your-key-here"

# Convert with AI refinement
uv run python -m docvert.cli.main convert ./myfile.pdf --output-dir ./results --llm-refiner
```

### Using local AI (Ollama) — works offline

Install [Ollama](https://ollama.com/), then:

```bash
# Download a model (one-time)
ollama pull llama3

# Set environment variables
export OPENAI_API_KEY="dummy"
export OPENAI_BASE_URL="http://localhost:11434/v1"

# Convert with AI refinement
uv run python -m docvert.cli.main convert ./myfile.pdf --output-dir ./results --llm-refiner
```

---

## FAQ

### Q: "command not found: uv"

Close Terminal completely and reopen it. If that doesn't work:

```bash
source $HOME/.local/bin/env
```

### Q: "pdfinfo not found"

The PDF extraction tool is missing:

- **macOS (Homebrew):** `brew install poppler`
- **macOS (MacPorts):** `sudo port install poppler`
- **Ubuntu/Debian:** `sudo apt install -y poppler-utils`
- **Fedora/RHEL:** `sudo dnf install -y poppler-utils`

### Q: "tesseract is not installed"

The OCR tool is missing:

- **macOS (Homebrew):** `brew install tesseract`
- **macOS (MacPorts):** `sudo port install tesseract`
- **Ubuntu/Debian:** `sudo apt install -y tesseract-ocr`
- **Fedora/RHEL:** `sudo dnf install -y tesseract`

### Q: Do I need to install Python?

No. `uv` automatically downloads and manages the correct Python version.

### Q: How do I update DocVert?

```bash
cd docvert
git pull
uv sync
```
