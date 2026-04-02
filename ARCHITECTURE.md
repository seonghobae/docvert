# Architecture

> **DocVert** — LLM-powered CLI tool for converting DOCX and PDF files to clean, semantic Markdown.

## High-Level Data Flow

```
Input files (DOCX / PDF)
        │
        ▼
  ┌───────────┐
  │  Parsers   │  docx_parser.py / pdf_parser.py
  └─────┬─────┘
        │  Document (blocks: Heading | Paragraph | Table | Image)
        ▼
  ┌───────────┐
  │  Refiner   │  agent/refiner.py  (optional, LLM-powered)
  └─────┬─────┘
        │  Refined Markdown string
        ▼
  ┌───────────┐
  │  Writer    │  core/writer.py
  └─────┬─────┘
        │  .md file + sidecar .json + extracted images
        ▼
     Output directory
```

The `BatchProcessor` (`core/batch.py`) orchestrates the pipeline for
one or many files and writes a summary CSV and JSON report.

## Package Layout

```
docvert/
├── __init__.py            # Package root — exposes __version__
├── cli/
│   └── main.py            # argparse CLI — `convert` and `batch` sub-commands
├── models/
│   ├── config.py          # DocvertConfig (Pydantic) — all processing options
│   └── document.py        # Block hierarchy: Block, Heading, Paragraph, Table, Image, Document
├── parsers/
│   ├── docx_parser.py     # DOCX → Document  (python-docx + mammoth fallback)
│   └── pdf_parser.py      # PDF  → Document  (docling → unstructured fallback)
├── core/
│   ├── batch.py           # BatchProcessor — orchestrates parse → refine → write
│   └── writer.py          # Writer — Markdown files, sidecar JSON, image assets
└── agent/
    └── refiner.py         # LLMRefiner — optional LLM post-processing via litellm
```

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Dataclass block model** (`document.py`) | Lightweight, stdlib-only representation; `to_markdown()` renders the full document without external deps. |
| **Pydantic config** (`config.py`) | Validated, typed configuration with sensible defaults. Shared across CLI, parsers, and batch processor. |
| **Graceful fallback parsers** | DOCX: python-docx primary, mammoth fallback. PDF: docling primary, unstructured fallback. Neither dependency is hard-required — import errors are caught at module level. |
| **Optional LLM refinement** | The `--llm-refiner` flag activates `LLMRefiner` via litellm; the pipeline works fully offline without it. |
| **Hash-based caching** | `BatchProcessor` can skip already-processed files using MD5 hashes when `--cache` is passed. |
| **Standard Markdown tables** | Tables render with a header separator row (`| --- | --- |`) so they display correctly in all Markdown renderers. |

## CI / CD

| Workflow | File | Trigger |
|---|---|---|
| **CI** | `.github/workflows/ci.yml` | Push / PR to `master` |
| **Publish Docs** | `.github/workflows/pages.yml` | Push to `master` |
| **Create Release** | `.github/workflows/release.yml` | Push `v*` tag |

CI enforces: ruff lint, mypy `--strict`, interrogate 100% docstring coverage, pytest 100% line coverage.

## Quality Gates

- **100 % test coverage** — `pytest --cov-fail-under=100`
- **100 % docstring coverage** — `interrogate -f 100`
- **Strict type checking** — `mypy --strict`
- **Lint** — `ruff check`

## Dependencies

- **Runtime**: `python-docx`, `mammoth`, `pydantic`, `loguru`, `litellm` (optional LLM)
- **PDF extras**: `docling` and/or `unstructured` (both optional, graceful fallback)
- **Build**: `hatchling`
- **Dev / Test**: `pytest`, `pytest-cov`, `ruff`, `mypy`, `interrogate`, `mkdocs-material`
