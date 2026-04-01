# DocVert User Guide

## What is DocVert?

Imagine you have a PDF report or a Word (DOCX) file from work. DocVert extracts the content and converts it into a clean **text file** that preserves the document structure (headings, tables, lists).

The output is saved as **Markdown (.md)** — a simple text format you can open with any text editor (Notepad, TextEdit, VS Code, etc.).

**When is DocVert useful?**

- PDF text is garbled when you try to copy-paste it
- You need to convert Word files into a format other systems can use
- You have many documents to convert at once

---

## Before You Start

### What is a "Terminal"?

It's a program where you type commands as text instead of clicking buttons. Don't worry — you'll just **copy and paste** the commands from this guide. Almost no typing required.

### How to copy and paste

| OS | Copy | Paste |
|---|---|---|
| Mac | `Cmd + C` | `Cmd + V` |
| Windows (WSL terminal) | Select text to auto-copy | Right-click |
| Linux | `Ctrl + Shift + C` | `Ctrl + Shift + V` |

> **Important:** In a terminal, `Ctrl + C` does NOT copy — it stops the running program!
> On Linux/WSL, always use `Ctrl + Shift + C` to copy.

### After pasting a command

Press **Enter** to run it.

### When asked for a password

Some commands start with `sudo`, which asks for your password. When you type the password, **nothing shows on screen** — no dots, no asterisks. This is normal. Just type it and press Enter.

---

## Which installation method?

| Your computer | Go to |
|---|---|
| **Mac** | [Mac Installation](#mac-installation) |
| **Windows** | [Windows Installation](#windows-installation) |
| **Linux** | [Linux Installation](#linux-installation) |
| **No internet** (air-gapped) | [Offline Installation](#offline-installation) |

> **About Docker Desktop:** There is also a Docker-based installation method, but Docker Desktop **permanently uses 2-4GB+ of RAM** whenever your computer is on. This is heavy for casual users, so this guide recommends **native installation without Docker** for Mac, Windows, and Linux. Docker is only used for the offline/air-gapped scenario.

---

## Mac Installation

### Step 1: Open Terminal

1. Press `Cmd + Space` (a search bar appears in the center of the screen).
2. Type `Terminal`.
3. Click on **Terminal** in the results.

> A window with a blinking cursor on a dark (or white) background opens. This is where you'll paste all commands.

### Step 2: Install Developer Tools

Paste this and press Enter:

```bash
xcode-select --install
```

**What happens:** A popup appears. Click **"Install"** and wait 5-10 minutes.

**If it says "already installed":** That's fine. Move to the next step.

### Step 3: Install Homebrew

Homebrew is a tool that makes it easy to install programs on Mac.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**What happens:** Installation progress is shown. It may ask for your Mac login password.

**After it finishes:** You'll see `==> Next steps:` at the bottom. **You must** copy and run the commands shown there. They usually look like:

```bash
echo >> ~/.zprofile
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**Verify it worked:**

```bash
brew --version
```

If you see `Homebrew 4.x.x`, it's working.

### Step 4: Install Required Programs

```bash
brew install poppler tesseract libmagic
```

**What happens:** Programs are downloaded and installed (1-3 minutes).

> **What are these?**
>
> - `poppler` — extracts text from PDF files
> - `tesseract` — reads text from images (OCR)
> - `libmagic` — detects file types automatically

### Step 5: Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**After this, close Terminal completely and reopen it** (required!).

> **What is uv?** It automatically installs and manages the Python environment DocVert needs. You do NOT need to install Python yourself.

### Step 6: Download DocVert

```bash
git clone https://github.com/seonghobae/docvert.git
```

**What you see:**

```
Cloning into 'docvert'...
remote: Enumerating objects: ...
Receiving objects: 100% ...
```

Now enter the downloaded folder:

```bash
cd docvert
```

> **What does `cd` mean?** "Change directory" — it moves you into the `docvert` folder.

Install the required libraries:

```bash
uv sync
```

**What happens:** Libraries are downloaded (2-5 minutes the first time).

### Step 7: Verify Installation

```bash
uv run python -m docvert.cli.main --help
```

**If successful, you see:**

```
usage: python3 -m docvert.cli.main [-h] {convert,batch} ...

Docvert: Convert documents to Markdown.
```

Installation complete! Go to [How to Use DocVert](#how-to-use-docvert).

---

## Windows Installation

On Windows, you first install **WSL** (Windows Subsystem for Linux) — an official Microsoft feature that lets you run Linux inside Windows.

### Step 1: Install WSL

1. Click the **Start button** (bottom-left corner).
2. Type `PowerShell`.
3. **Right-click** on "Windows PowerShell" → **"Run as Administrator"**.
4. Click **"Yes"** when asked to allow changes.
5. In the blue PowerShell window, paste this and press Enter:

```cmd
wsl --install
```

6. **Restart your computer** when prompted.

**After restart:** An Ubuntu window opens automatically. Set up:

- **Username:** Type any lowercase name (e.g., `myname`)
- **Password:** Type any password. **Nothing shows on screen — that's normal.** Type it and press Enter. Type it again to confirm.

> Requires **Windows 10 (version 2004+)** or **Windows 11**.
> Check: Start → Settings → System → About → "Windows specifications"

### Step 2: Install Required Programs

In the Ubuntu terminal (black window):

```bash
sudo apt update
```

Enter the password you set in Step 1 (nothing shows — normal).

```bash
sudo apt install -y poppler-utils tesseract-ocr libmagic-dev curl git
```

### Step 3: Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### Step 4: Download DocVert

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

### Step 5: Verify

```bash
uv run python -m docvert.cli.main --help
```

If you see the help text, go to [How to Use DocVert](#how-to-use-docvert).

### Finding Your Windows Files from WSL

| Windows path | WSL path |
|---|---|
| `C:\Users\John\Desktop\` | `/mnt/c/Users/John/Desktop/` |
| `C:\Users\John\Documents\` | `/mnt/c/Users/John/Documents/` |
| `D:\Work\` | `/mnt/d/Work/` |

> Don't know your username? Open File Explorer and look at `C:\Users\`.

---

## Linux Installation

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y poppler-utils tesseract-ocr libmagic-dev curl git
```

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

```bash
git clone https://github.com/seonghobae/docvert.git
cd docvert
uv sync
```

Verify: `uv run python -m docvert.cli.main --help`

### Fedora / RHEL / CentOS

```bash
sudo dnf install -y poppler-utils tesseract libmagic curl git
```

Then same as Ubuntu (`curl ... uv` → `git clone ...` → `uv sync`).

---

## Offline Installation

For secure networks with no internet access. Requires Docker or Podman on the target machine.

### What you need

- One computer WITH internet
- USB drive (4GB+ recommended)
- Docker or Podman on the air-gapped machine

### On the internet-connected computer

1. Open [https://github.com/seonghobae/docvert/releases](https://github.com/seonghobae/docvert/releases) in a browser.
2. Find the latest version at the top.
3. Download ALL files named `docvert-offline-release.tar.gz.part-aa`, `part-ab`, `part-ac`, etc.
4. Copy them to a USB drive.

### On the air-gapped machine

```bash
# Go to where the files are
cd /path/to/usb/files

# Combine split files into one
cat docvert-offline-release.tar.gz.part-* > docvert-offline-release.tar.gz

# Extract
tar -xzvf docvert-offline-release.tar.gz
cd docvert-offline-release

# Install into Docker
docker load -i docvert-offline.tar.gz
```

**Verify:** `docker images | grep docvert` — if you see `docvert`, it worked!

### Using it offline

```bash
docker run --rm -v "$(pwd)":/data docvert:offline convert /data/report.pdf --output-dir /data/results
```

---

## How to Use DocVert

### Convert a single PDF file

**Scenario:** You have `report.pdf` on your Desktop and want to convert it.

**On Mac:**

```bash
cd ~/Desktop
uv run python -m docvert.cli.main convert ./report.pdf --output-dir ./results
```

**On Windows (WSL):**

```bash
cd /mnt/c/Users/YourName/Desktop
uv run python -m docvert.cli.main convert ./report.pdf --output-dir ./results
```

> **What each part means:**
>
> | Part | Meaning |
> |---|---|
> | `uv run python -m docvert.cli.main` | Run the DocVert program |
> | `convert` | "Convert one file" |
> | `./report.pdf` | The file to convert |
> | `--output-dir ./results` | Where to save the output (auto-created) |

**If successful:**

```
Processing 1 files...
Processed 1 files. Failures: 0. Warnings: 0
```

### Convert a Word (DOCX) file

```bash
uv run python -m docvert.cli.main convert ./meeting-notes.docx --output-dir ./results
```

### Convert all files in a folder

```bash
uv run python -m docvert.cli.main batch ./my_documents --output-dir ./results
```

> `batch` automatically finds and converts ALL PDF and DOCX files in the folder, including subfolders.

### What you get after conversion

```
results/
├── report.md              ← converted text file (open with any text editor)
├── report.conversion.json ← conversion details (parser used, warnings)
└── report.assets/         ← images extracted from the document
    ├── image_0.png
    └── image_1.png
```

---

## Troubleshooting

### "command not found: uv"

Close Terminal completely and reopen. If that doesn't work:

```bash
source $HOME/.local/bin/env
```

### "command not found: git"

- **Mac:** Run `xcode-select --install` again
- **Ubuntu/Debian:** `sudo apt install -y git`
- **Fedora/RHEL:** `sudo dnf install -y git`

### "pdfinfo not found"

- **Mac:** `brew install poppler`
- **Ubuntu/Debian:** `sudo apt install -y poppler-utils`

### "tesseract is not installed"

- **Mac:** `brew install tesseract`
- **Ubuntu/Debian:** `sudo apt install -y tesseract-ocr`

### Do I need to install Python?

No. `uv` downloads it automatically.

### How do I update DocVert?

```bash
cd docvert
git pull
uv sync
```

### "No such file or directory" when I type `cd docvert`

DocVert is probably in your home folder:

```bash
cd ~/docvert
```
