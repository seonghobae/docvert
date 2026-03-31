# ADR 0001: Selection of Primary and Fallback Parsers for DOCX and PDF

**Date:** 2026-03-31  
**Status:** Accepted  

## Context

**Docvert** is tasked with converting DOCX and PDF documents into clean, semantic Markdown. Preserving the document structure (headings, lists, bold/italic text, tables) and extracting embedded visual elements (images) are critical requirements. Because documents encountered in the wild have highly variable formatting, styling, and structural integrity, relying on a single parsing library per format poses a high risk of failure or data loss.

We need to choose parsing libraries for both DOCX and PDF that offer high fidelity, while establishing a robust fallback mechanism for edge cases.

## Decision

We have decided to implement a dual-parser strategy for each file type:

### DOCX Parsers
1. **Primary: `python-docx` (with heuristic heading detection)**
   - **Why:** `python-docx` provides granular, low-level access to the internal XML structure of Word documents. This allows us to apply custom heuristic rules to detect implicit headings (e.g., bold text with large font sizes that lack official "Heading" styles) and accurately extract complex elements like tables and nested lists.
2. **Fallback: `mammoth`**
   - **Why:** `mammoth` is specifically designed for converting DOCX to HTML/Markdown by mapping styles directly. While it can struggle with non-standard, implicitly styled documents (hence not being the primary choice), it is extremely fast and robust for well-styled documents. It serves as an excellent, stable fallback when our `python-docx` heuristics fail or encounter corrupted XML.

### PDF Parsers
1. **Primary: `docling`**
   - **Why:** `docling` is a state-of-the-art PDF parsing engine built for high-fidelity extraction. It excels at recognizing layout structures, reading order, tables, and nested components in modern PDFs, making it ideal for our goal of producing semantic Markdown.
2. **Fallback: `unstructured`**
   - **Why:** The `unstructured` library provides a highly resilient, ML-backed approach to document parsing. In cases where a PDF is essentially a collection of scanned images or has an impenetrable layout layer that trips up `docling`, `unstructured` can fall back to OCR and partition models to salvage the text and structural metadata.

## Consequences

### Positive
- **Increased Robustness:** The fallback mechanism ensures that Docvert will succeed on a much wider variety of documents than single-parser tools.
- **Data Quality:** By using `python-docx` and `docling` as primaries, we optimize for the best possible semantic layout and structure preservation.
- **Graceful Degradation:** When a primary parser fails, the sidecar JSON file will log the fallback event and any associated confidence score drops, giving users visibility into the conversion quality.

### Negative
- **Dependency Bloat:** Including multiple parser backends (`docling`, `unstructured`, `python-docx`, `mammoth`) increases the size of the project dependencies and the Docker image footprint.
- **Maintenance Overhead:** The development team must maintain two separate processing pipelines for each document type, requiring more comprehensive testing (though mitigated by our 100% test coverage requirement).

## Alternatives Considered
- *Pandoc:* While powerful, Pandoc requires a system-level binary installation (not pure Python), making containerization and cross-platform CLI distribution more complex.
- *PyPDF2 / pdfplumber:* These are excellent for basic text extraction but severely lack the layout analysis and structural awareness required to generate semantic Markdown.