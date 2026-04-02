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

You can run the CLI in multiple ways:

```bash
# Using the installed entry point (after uv sync or pip install)
docvert [COMMAND] [OPTIONS]

# Using uv run (recommended during development)
uv run python -m docvert.cli.main [COMMAND] [OPTIONS]

# Using standard Python module invocation
python -m docvert.cli.main [COMMAND] [OPTIONS]
```

### Global Options

These options are available at the top level (before any subcommand):

| Option | Description |
|---|---|
| `-h`, `--help` | Show help message and exit. |
| `-V`, `--version` | Show the installed Docvert version and exit. |

**Example — check version:**
```bash
docvert -V
# docvert 0.2.2
```

### Commands

#### `convert`
Convert a single DOCX or PDF file to Markdown.

**Arguments:**
- `input`: Path to the input DOCX or PDF file.

**Options:**

| Option | Description | Default |
|---|---|---|
| `--output-dir` | Directory to save the generated `.md`, `.json`, and assets. | `./out` |
| `--llm-refiner` | Flag to use LLM to refine the markdown output. | off |
| `--llm-model` | The LLM model to use for refinement. | `gpt-4o-mini` |

**Example:**
```bash
python -m docvert.cli.main convert ./docs/sample.pdf --output-dir ./results --llm-refiner
python -m docvert.cli.main convert ./docs/sample.pdf --llm-refiner --llm-model gpt-4o
```

#### `batch`
Process a directory of DOCX and/or PDF files, with built-in caching.

**Arguments:**
- `input_dir`: Path to the directory containing input files.

**Options:**

| Option | Description | Default |
|---|---|---|
| `--output-dir` | Directory to save all outputs. Subdirectories matching the source structure will be created. | `./out` |
| `--llm-refiner` | Flag to use LLM to refine the markdown output. | off |
| `--llm-model` | The LLM model to use for refinement. | `gpt-4o-mini` |
| `--continue-on-error` / `--no-continue-on-error` | Continue processing if a file fails. | on |
| `--cache` | Use hashing to skip already processed files. | off |

**Example:**
```bash
python -m docvert.cli.main batch ./company_docs --output-dir ./processed_docs --continue-on-error --cache
```

### Conversion Configuration Options

The following options are shared between `convert` and `batch` subcommands. They control how documents are parsed and what the output contains.

#### Language & OCR

| Option | Choices | Default | Description |
|---|---|---|---|
| `--language-hint` | `ko`, `en`, `auto` | `auto` | Primary language hint for the document. |
| `--ocr-languages` | space-separated list | `ko en` | Languages to use when OCR is performed. |

**Example:**
```bash
# Process a Japanese document with Japanese+English OCR
python -m docvert.cli.main convert ./doc.pdf --language-hint auto --ocr-languages ja en
```

#### Document Element Handling

| Option | Choices | Default | Description |
|---|---|---|---|
| `--heading-mode` | `auto`, `style_only`, `heuristic` | `auto` | Strategy for identifying headings. `auto` tries style-based detection first, then falls back to heuristics. |
| `--comment-mode` | `preserve`, `appendix`, `inline`, `drop` | `preserve` | How to handle document comments. |
| `--footnote-mode` | `preserve`, `appendix`, `inline` | `preserve` | How to handle footnotes. |
| `--image-mode` | `extract_link`, `embed`, `extract_with_ocr`, `skip` | `extract_link` | How to handle images. `extract_link` saves images to the assets directory and links them. |
| `--table-mode` | `markdown_preferred`, `html_for_complex` | `markdown_preferred` | Formatting preference for tables. Complex tables may use HTML if `html_for_complex` is selected. |
| `--pdf-reading-order-mode` | `auto`, `layout_strict`, `ocr_fallback` | `auto` | Reading order strategy for PDFs. `layout_strict` preserves the visual layout order. |

#### Boolean Flags

These flags use `--flag` / `--no-flag` syntax (e.g. `--normalize-heading-levels` to enable, `--no-normalize-heading-levels` to disable).

| Flag | Default | Description |
|---|---|---|
| `--include-headers-footers` | off | Include headers and footers from the document in the output. |
| `--normalize-heading-levels` | on | Normalize heading levels to start from h1. |
| `--preserve-numbering` | on | Keep numbering for ordered lists and headings. |
| `--deterministic` | on | Produce deterministic output (disables non-deterministic LLM sampling). |
| `--aggressive-heading-inference` | off | Aggressively infer headings based on styling (bold, font size, etc.). |

**Example:**
```bash
# Extract with OCR on images, include headers/footers, aggressive heading detection
python -m docvert.cli.main convert ./scan.pdf \
  --image-mode extract_with_ocr \
  --include-headers-footers \
  --aggressive-heading-inference \
  --no-normalize-heading-levels
```

## LLM Configuration

Docvert uses `litellm` under the hood for its `--llm-refiner` feature. This allows you to use almost any LLM provider natively without changing the codebase.

By default, it uses `gpt-4o-mini` via OpenAI. You can change the model with the `--llm-model` option:

```bash
# Use GPT-4o instead of the default gpt-4o-mini
python -m docvert.cli.main convert ./doc.pdf --llm-refiner --llm-model gpt-4o

# Use Claude via litellm
python -m docvert.cli.main convert ./doc.pdf --llm-refiner --llm-model claude-3-5-sonnet-20241022
```

**Using OpenAI:**
```bash
export OPENAI_API_KEY="your-api-key"
```

**Using Vertex AI:**
```bash
export VERTEX_PROJECT="your-google-project"
export VERTEX_LOCATION="us-central1"
# Ensure you are authenticated via gcloud auth application-default login
```

**Using Local Models (e.g. Ollama):**
```bash
export OPENAI_API_KEY="dummy"
export OPENAI_BASE_URL="http://localhost:11434/v1"
python -m docvert.cli.main convert ./doc.pdf --llm-refiner --llm-model llama3
```

You can pass the appropriate environment variables corresponding to the provider you wish to use as per the [litellm documentation](https://docs.litellm.ai/).

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
