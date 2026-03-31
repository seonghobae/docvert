"""PDF document parser module."""

from pathlib import Path
from typing import Optional
from loguru import logger

from docvert.models.document import Document, Paragraph, Heading, Table
from docvert.models.config import DocvertConfig

try:
    from docling.document_converter import DocumentConverter

    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

try:
    from unstructured.partition.pdf import partition_pdf

    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False


class PdfParser:
    """Parser for PDF files.

    Uses `docling` as the primary parser if available. If `docling` fails or is not
    installed, falls back to `unstructured`.

    Args:
        config (Optional[DocvertConfig]): Configuration object for parsing options.
    """

    def __init__(self, config: Optional[DocvertConfig] = None):
        self.config = config or DocvertConfig()

    def parse(self, file_path: str | Path) -> Document:
        """Parses a PDF file into a Document object.

        Args:
            file_path (str | Path): Path to the PDF file.

        Returns:
            Document: The parsed document structure containing headings, paragraphs, and tables.

        Raises:
            FileNotFoundError: If the specified PDF file does not exist.
            RuntimeError: If both `docling` and `unstructured` parsers fail or are unavailable.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            if DOCLING_AVAILABLE:
                logger.info(f"Parsing PDF with Docling: {file_path}")
                return self._parse_with_docling(file_path)
            else:
                logger.warning("Docling not available, skipping primary parser.")
                raise ImportError("Docling not available")
        except Exception as e:
            logger.warning(
                f"Docling parsing failed: {e}. Falling back to unstructured."
            )
            if UNSTRUCTURED_AVAILABLE:
                logger.info(f"Parsing PDF with Unstructured: {file_path}")
                return self._parse_with_unstructured(file_path)
            else:
                logger.error(
                    "Unstructured not available. PDF parsing failed completely."
                )
                raise RuntimeError(
                    f"Could not parse PDF. Both parsers failed or missing. Original error: {e}"
                )

    def _parse_with_docling(self, file_path: Path) -> Document:
        """Parses a PDF file using the `docling` library.

        Args:
            file_path (Path): Path to the PDF file.

        Returns:
            Document: The parsed document structure.
        """
        converter = DocumentConverter()
        result = converter.convert(file_path)

        doc = Document()

        try:
            # Attempt to iterate over docling document items for full adherence
            items_found = False
            if hasattr(result.document, "iterate_items"):
                for item, level in result.document.iterate_items():
                    items_found = True
                    item_type = type(item).__name__

                    if item_type == "TextItem":
                        label = getattr(item, "label", "text")
                        if str(label) in ("title", "section_header"):
                            doc.blocks.append(
                                Heading(content=item.text, level=1, score=100)  # type: ignore
                            )
                        else:
                            doc.blocks.append(Paragraph(content=item.text))  # type: ignore
                    elif item_type == "TableItem":
                        md_table = item.export_to_markdown()  # type: ignore
                        doc.blocks.append(Table(content=md_table, rows=[]))
                    elif hasattr(item, "text") and item.text:  # type: ignore
                        doc.blocks.append(Paragraph(content=item.text))  # type: ignore

            if not items_found:
                raise ValueError("No items yielded by iterate_items")

        except Exception as e:
            logger.info(
                f"Could not parse docling blocks precisely ({e}), falling back to raw markdown block."
            )
            md_text = result.document.export_to_markdown()
            doc.blocks.append(
                Paragraph(content=md_text, metadata={"format": "markdown"})
            )

        return doc

    def _parse_with_unstructured(self, file_path: Path) -> Document:
        """Parses a PDF file using the `unstructured` library.

        Args:
            file_path (Path): Path to the PDF file.

        Returns:
            Document: The parsed document structure.
        """
        languages = (
            self.config.ocr_languages
            if hasattr(self.config, "ocr_languages")
            else ["eng"]
        )

        # unstructured expects language strings like "eng", "kor" in some cases, but auto-maps in newer versions.
        # We will pass what we have.

        try:
            elements = partition_pdf(
                filename=str(file_path),
                strategy="auto",
                languages=languages,
            )

            # If nothing extracted, it might be a scanned PDF requiring hi_res or ocr_only
            if not elements:
                logger.info("No text extracted with auto strategy, trying ocr_only")
                elements = partition_pdf(
                    filename=str(file_path),
                    strategy="ocr_only",
                    languages=languages,
                )
        except Exception as e:
            logger.warning(f"Unstructured auto strategy failed: {e}. Trying ocr_only.")
            elements = partition_pdf(
                filename=str(file_path),
                strategy="ocr_only",
                languages=languages,
            )

        doc = Document()
        for element in elements:
            element_type = getattr(element, "category", type(element).__name__)
            text = str(element).strip()

            if not text:
                continue

            metadata = {"source": "unstructured", "type": element_type}

            if element_type == "Title":
                doc.blocks.append(
                    Heading(content=text, level=1, score=100, metadata=metadata)
                )
            elif element_type == "Table":
                if hasattr(element, "metadata") and hasattr(
                    element.metadata, "text_as_html"
                ):
                    metadata["text_as_html"] = element.metadata.text_as_html
                doc.blocks.append(Table(content=text, metadata=metadata))
            else:
                doc.blocks.append(Paragraph(content=text, metadata=metadata))

        return doc
