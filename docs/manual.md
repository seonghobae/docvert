# Docvert User Manual

Welcome to the **Docvert** User Manual. This guide details how to use the CLI, explains the available configuration options, and provides an overview of the system's architecture.

## Overview

Docvert is designed to handle complex document structures from DOCX and PDF formats and output clean, semantically correct Markdown (`.md`). It accomplishes this by utilizing primary document parsers (`python-docx` for DOCX, `docling` for PDF) and automatically falling back to alternatives (`mammoth`, `unstructured`) when necessary. 

Every processed document yields:
1. `document.md`: The semantic Markdown output.
2. `document.conversion.json`: A sidecar file containing metadata, parser used, hash, and warnings.
3. `/document.assets/`: A directory for extracted assets related to the document.

## CLI Usage

The Docvert CLI exposes commands to run conversions on single files or process batches of files.

You can run the CLI using standard Python or via environment managers like `uv`.

```bash
# Using standard Python (if installed globally or in an active venv)
python -m docvert.cli.main [COMMAND] [OPTIONS]

# Using uv
uv run python -m docvert.cli.main [COMMAND] [OPTIONS]
```

### Commands

#### `convert`
Convert a single DOCX or PDF file to Markdown.

**Arguments:**
- `input`: Path to the input DOCX or PDF file.

**Options:**
- `--output-dir`: Directory to save the generated `.md`, `.json`, and assets. (Default: `./out`)
- `--llm-refiner`: Flag to use LLM to refine the markdown output.

**Example:**
```bash
python -m docvert.cli.main convert ./docs/sample.pdf --output-dir ./results --llm-refiner
```

#### `batch`
Process a directory of DOCX and/or PDF files, with built-in caching.

**Arguments:**
- `input_dir`: Path to the directory containing input files.

**Options:**
- `--output-dir`: Directory to save all outputs. Subdirectories matching the source structure will be created. (Default: `./out`)
- `--continue-on-error`: Continue processing if a file fails.
- `--cache`: Use hashing to skip already processed files.
- `--llm-refiner`: Flag to use LLM to refine the markdown output.

**Example:**
```bash
python -m docvert.cli.main batch ./company_docs --output-dir ./processed_docs --continue-on-error --cache
```

## Sidecar JSON Structure

Alongside every `output.md`, Docvert generates an `output.conversion.json` sidecar. This provides programmatic insight into the parsing quality:

```json
{
  "confidence": 1.0,
  "file_hash": "d41d8cd98f00b204e9800998ecf8427e",
  "input_format": ".docx",
  "llm_refined": false,
  "output_file": "out/sample.md",
  "parser_path_used": "DocxParser",
  "source_file": "sample.docx",
  "warnings": []
}
```

## Architecture

Docvert is built with a modular, pipeline-based architecture, strongly typed via `pydantic`.

1. **CLI Layer (`docvert.cli`)**: Handles user input, argument parsing, and command routing.
2. **Core Layer (`docvert.core`)**: 
   - `BatchProcessor`: Orchestrates the parsing process. It checks the cache via file hashing, decides which parser to instantiate, and optionally invokes the LLM refiner.
   - `Writer`: Writes the output Markdown, the sidecar `.conversion.json`, and manages asset directories.
3. **Parser Engines (`docvert.parsers`)**:
   - `DocxParser`: Uses `python-docx` for primary processing (employing heuristic heading detection) and `mammoth` as a fallback.
   - `PdfParser`: Uses `docling` for primary PDF processing and `unstructured` as a fallback.
4. **Agent Layer (`docvert.agent`)**:
   - `LLMRefiner`: An optional, LLM-powered post-processor that cleans up the Markdown output, fixes semantic structure, and addresses obvious OCR or parsing errors.

All data structures passing between these layers are modeled in `docvert.models`, ensuring that developers and LLM agents working with the codebase can rely on predictable inputs and outputs.
