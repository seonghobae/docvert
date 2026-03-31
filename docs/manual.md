# Docvert User Manual

Welcome to the **Docvert** User Manual. This guide details how to use the CLI, explains the available configuration options, and provides an overview of the system's architecture.

## Overview

Docvert is designed to handle complex document structures from DOCX and PDF formats and output clean, semantically correct Markdown (`.md`). It accomplishes this by utilizing primary document parsers (`python-docx` for DOCX, `docling` for PDF) and automatically falling back to alternatives (`mammoth`, `unstructured`) when necessary. 

Every processed document yields:
1. `document.md`: The semantic Markdown output.
2. `document.json`: A sidecar file containing metadata, parsing confidence scores, and warnings.
3. `/images/`: A directory with extracted images (if the document contains visuals).

## CLI Usage

The Docvert CLI exposes commands to run conversions on single files or process batches of files.

You can run the CLI using standard Python or via environment managers like `uv` or `poetry`.

```bash
# Using standard Python (if installed globally or in an active venv)
python -m docvert.cli.main [COMMAND] [OPTIONS]

# Using uv
uv run python -m docvert.cli.main [COMMAND] [OPTIONS]

# Using poetry
poetry run python -m docvert.cli.main [COMMAND] [OPTIONS]
```

### Commands

#### `convert`
Convert a single DOCX or PDF file to Markdown.

**Arguments:**
- `FILE`: Path to the input DOCX or PDF file.

**Options:**
- `--output-dir`, `-o`: Directory to save the generated `.md`, `.json`, and images. (Default: `./output`)
- `--force`, `-f`: Ignore cache and force reprocessing of the file.
- `--verbose`, `-v`: Enable detailed logging.

**Example:**
```bash
python -m docvert.cli.main convert ./docs/sample.pdf -o ./results -v
```

#### `batch`
Process a directory of DOCX and/or PDF files, with built-in caching.

**Arguments:**
- `DIR`: Path to the directory containing input files.

**Options:**
- `--output-dir`, `-o`: Directory to save all outputs. Subdirectories matching the source structure will be created. (Default: `./output`)
- `--workers`, `-w`: Number of parallel workers for processing. (Default: 4)
- `--force`, `-f`: Ignore cache and force reprocessing of all files.

**Example:**
```bash
python -m docvert.cli.main batch ./company_docs -o ./processed_docs --workers 8
```

## Sidecar JSON Structure

Alongside every `output.md`, Docvert generates an `output.json` sidecar. This provides programmatic insight into the parsing quality:

```json
{
  "source_file": "sample.docx",
  "parser_used": "python-docx",
  "fallback_triggered": false,
  "confidence_score": 0.95,
  "metadata": {
    "author": "Jane Doe",
    "created_at": "2023-10-01T12:00:00Z"
  },
  "warnings": [
    "Unrecognized styling at paragraph 14, defaulting to standard text."
  ]
}
```

## Architecture

Docvert is built with a modular, pipeline-based architecture, strongly typed via `pydantic`.

1. **CLI Layer (`docvert.cli`)**: Handles user input, argument parsing, and logging configuration.
2. **Controller/Agent Layer (`docvert.agent`)**: Orchestrates the parsing process. It checks the cache, decides which parser to instantiate, and manages fallback logic if a primary parser fails or returns a low confidence score.
3. **Parser Engines (`docvert.parsers`)**:
   - `DocxParser`: Uses `python-docx` for primary processing (employing heuristic heading detection) and `mammoth` as a fallback.
   - `PdfParser`: Uses `docling` for primary PDF processing and `unstructured` as a fallback.
4. **Post-Processor (`docvert.postprocessor`)**: Cleans up the Markdown output, standardizes heading levels, and ensures image references correctly point to the locally extracted `/images` directory.
5. **Output Generator (`docvert.writer`)**: Writes the `.md`, the sidecar `.json`, and saves extracted images to disk.

All data structures passing between these layers are validated by `pydantic` models, ensuring that developers and LLM agents working with the codebase can rely on predictable inputs and outputs.