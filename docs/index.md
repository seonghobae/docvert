# DocVert

**DocVert** is an intelligent, LLM-powered CLI tool and agent for converting DOCX and PDF documents into clean, semantic Markdown. It focuses heavily on preserving document structure, headings, lists, and visual elements, while extracting key document metadata into sidecar JSON files.

## Features

- **Robust DOCX Parsing**: Primary parsing using `python-docx` with heuristic heading detection. Fallback to `mammoth` for difficult layouts.
- **Advanced PDF Parsing**: High-fidelity PDF extraction using `docling` as the primary engine. Fallback to `unstructured` for edge cases.
- **Rich Output Format**:
  - Generates clean, semantic `.md` files.
  - Produces a sidecar `.json` file containing extraction confidence scores, metadata, and parsing warnings.
  - Automatically extracts and saves images referenced in the source documents.
- **Batch Processing & Caching**: Efficiently process large directories of files with built-in caching to avoid redundant parsing.
- **Provider-Agnostic LLM Refinement**: Uses `litellm` under the hood, natively supporting OpenAI, Vertex AI, Anthropic, Bedrock, and local models via Ollama. Just set the appropriate environment variables (e.g. `OPENAI_API_KEY`, `VERTEX_PROJECT`).
- **Air-Gapped / Offline Deployment**: Pre-built Docker images available via [GitHub Releases](https://github.com/seonghobae/docvert/releases) for secure, offline environments.
- **Developer Ready**:
  - 100% test coverage.
  - Robust type hints powered by `pydantic`.
  - Built-in CLI using modern Python tooling (`uv`).

## Quick Start

The easiest way to use DocVert is via **Docker**:

```bash
# Download from GitHub Releases or build from source
docker build -t docvert:offline .

# Convert a single file
docker run --rm -v $(pwd):/data \
    docvert:offline convert /data/input.pdf --output-dir /data/out
```

For detailed installation instructions on every OS (macOS, Windows, Linux) — including setups with **no Homebrew or package manager installed** — see:

- [Installation Guide (English)](installation-guide.md)
- [설치 가이드 (한국어)](web-manual-ko.md)

## Documentation

- [Installation Guide (English)](installation-guide.md) — Per-OS zero-setup installation
- [설치 가이드 (한국어)](web-manual-ko.md) — OS별 제로셋업 설치 안내
- [User Manual & CLI Reference](manual.md) — CLI usage, LLM configuration, architecture
- [Offline / Air-Gapped Deployment](operations/offline-release-runbook.md) — Runbook for secure environments
- [Architecture Decision Records](architecture-decision-records/0001-parser-choices.md) — Parser implementation choices

## GitHub Releases (Offline Bundles)

Pre-built Docker images for air-gapped environments are available at:

**[github.com/seonghobae/docvert/releases](https://github.com/seonghobae/docvert/releases)**

Each release includes split archive files (`.part-*`) that can be combined, extracted, and loaded into Docker on machines without internet access.

## License

MIT License
