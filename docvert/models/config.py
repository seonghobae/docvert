from typing import List, Literal
from pydantic import BaseModel, Field


class DocvertConfig(BaseModel):
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
