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
- **Provider-Agnostic LLM Refinement**: Uses `litellm` under the hood, natively supporting OpenAI, Vertex AI, Anthropic, Bedrock, and local models via Ollama.
- **Air-Gapped / Offline Deployment**: Pre-built Docker images via [GitHub Releases](https://github.com/seonghobae/docvert/releases) for secure, offline environments.
- **Developer Ready**:
  - 100% test coverage.
  - Robust type hints powered by `pydantic`.
  - Built-in CLI using modern Python tooling (`uv`).

## Quick Start (Docker — Recommended)

```bash
# Build from source
git clone https://github.com/seonghobae/docvert.git
cd docvert
docker build -t docvert:offline .

# Convert a file
docker run --rm -v $(pwd):/data \
    docvert:offline convert /data/input.pdf --output-dir /data/out
```

Or install natively — see the full [Installation Guide](https://seonghobae.github.io/docvert/installation-guide/).

## Documentation

Full documentation is available at **[seonghobae.github.io/docvert](https://seonghobae.github.io/docvert/)**

- [Installation Guide (English)](https://seonghobae.github.io/docvert/installation-guide/) — Per-OS zero-setup, no Homebrew required
- [설치 가이드 (한국어)](https://seonghobae.github.io/docvert/web-manual-ko/) — OS별 제로셋업 설치 안내
- [User Manual & CLI Reference](https://seonghobae.github.io/docvert/manual/) — CLI usage, LLM configuration, architecture
- [Offline Deployment Runbook](https://seonghobae.github.io/docvert/operations/offline-release-runbook/) — Air-gapped setup guide
- [Architecture Decision Records](https://seonghobae.github.io/docvert/architecture-decision-records/0001-parser-choices/) — Parser implementation choices

## GitHub Releases (Offline Bundles)

Pre-built Docker images for air-gapped environments:

**[github.com/seonghobae/docvert/releases](https://github.com/seonghobae/docvert/releases)**

## License

MIT License
