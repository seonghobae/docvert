# Docvert

**Docvert** is an intelligent, LLM-powered CLI tool and agent for converting DOCX and PDF documents into clean, semantic Markdown. It focuses heavily on preserving document structure, headings, lists, and visual elements, while extracting key document metadata into sidecar JSON files.

## Features

- **Robust DOCX Parsing**: Primary parsing using `python-docx` with heuristic heading detection. Fallback to `mammoth` for difficult layouts.
- **Advanced PDF Parsing**: High-fidelity PDF extraction using `docling` as the primary engine. Fallback to `unstructured` for edge cases.
- **Rich Output Format**: 
  - Generates clean, semantic `.md` files.
  - Produces a sidecar `.json` file containing extraction confidence scores, metadata, and parsing warnings.
  - Automatically extracts and saves images referenced in the source documents.
- **Batch Processing & Caching**: Efficiently process large directories of files with built-in caching to avoid redundant parsing.
- **Provider-Agnostic LLM Refinement**: Uses `litellm` under the hood, natively supporting OpenAI, Vertex AI, Anthropic, Bedrock, and local models via Ollama. Just set the appropriate environment variables (e.g. `OPENAI_API_KEY`, `VERTEX_PROJECT`).
- **Developer Ready**: 
  - 100% test coverage.
  - Robust type hints powered by `pydantic`.
  - Built-in CLI using modern Python tooling (`uv` or `poetry`).

## Quickstart

Ensure you have Python 3.10+ and [uv](https://github.com/astral-sh/uv) installed.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/docvert.git
   cd docvert
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Run the CLI**:
   Convert a single file easily using `uv run`:
   ```bash
   uv run python -m docvert.cli.main convert input.docx --output-dir ./out
   ```
   Or convert an entire directory:
   ```bash
   uv run python -m docvert.cli.main batch ./input_docs --output-dir ./out
   ```

## Documentation

- [User Manual & Architecture](docs/manual.md)
- [Architecture Decision Records (ADRs)](docs/architecture-decision-records/0001-parser-choices.md)

## License

MIT License