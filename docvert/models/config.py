"""Configuration model for Docvert document processing."""

from typing import List, Literal
from pydantic import BaseModel, Field


class DocvertConfig(BaseModel):
    """Configuration model for Docvert document processing.

    Attributes:
        language_hint (Literal["ko", "en", "auto"]): Primary language hint for the document.
        ocr_languages (List[str]): Languages to be used when OCR is performed.
        heading_mode (Literal["auto", "style_only", "heuristic"]): Strategy for identifying headings.
        comment_mode (Literal["preserve", "appendix", "inline", "drop"]): Strategy for handling document comments.
        footnote_mode (Literal["preserve", "appendix", "inline"]): Strategy for handling footnotes.
        image_mode (Literal["extract_link", "embed", "extract_with_ocr", "skip"]): Strategy for handling images.
        table_mode (Literal["markdown_preferred", "html_for_complex"]): Formatting preference for tables.
        pdf_reading_order_mode (Literal["auto", "layout_strict", "ocr_fallback"]): Reading order strategy for PDFs.
        include_headers_footers (bool): Whether to include headers and footers from the document.
        normalize_heading_levels (bool): Whether to normalize heading levels (e.g. h1, h2, etc.) to start from h1.
        preserve_numbering (bool): Whether to keep numbering for lists and headings.
        continue_on_error (bool): Whether to continue processing if a non-fatal error occurs.
        cache_by_hash (bool): Whether to cache processing results using document hash.
        deterministic (bool): Whether processing results should be deterministic.
        aggressive_heading_inference (bool): Whether to aggressively infer headings based on styling.
    """

    language_hint: Literal["ko", "en", "auto"] = "auto"
    ocr_languages: List[str] = Field(default_factory=lambda: ["ko", "en"])
    heading_mode: Literal["auto", "style_only", "heuristic"] = "auto"
    comment_mode: Literal["preserve", "appendix", "inline", "drop"] = "preserve"
    footnote_mode: Literal["preserve", "appendix", "inline"] = "preserve"
    image_mode: Literal["extract_link", "embed", "extract_with_ocr", "skip"] = (
        "extract_link"
    )
    table_mode: Literal["markdown_preferred", "html_for_complex"] = "markdown_preferred"
    pdf_reading_order_mode: Literal["auto", "layout_strict", "ocr_fallback"] = "auto"

    include_headers_footers: bool = False
    normalize_heading_levels: bool = True
    preserve_numbering: bool = True
    continue_on_error: bool = True
    cache_by_hash: bool = True
    deterministic: bool = True
    aggressive_heading_inference: bool = False

    use_llm_refiner: bool = False
    llm_model: str = "gpt-4o-mini"
