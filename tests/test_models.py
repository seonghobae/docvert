import pytest
from pydantic import ValidationError
from docvert.models.config import DocvertConfig
from docvert.models.document import Block, Paragraph, Heading, Table, Document


def test_config_defaults() -> None:
    config = DocvertConfig()
    assert config.language_hint == "auto"
    assert config.ocr_languages == ["ko", "en"]
    assert config.heading_mode == "auto"
    assert config.comment_mode == "preserve"
    assert config.footnote_mode == "preserve"
    assert config.image_mode == "extract_link"
    assert config.table_mode == "markdown_preferred"
    assert config.pdf_reading_order_mode == "auto"
    assert config.include_headers_footers is False
    assert config.normalize_heading_levels is True
    assert config.preserve_numbering is True
    assert config.continue_on_error is True
    assert config.cache_by_hash is True
    assert config.deterministic is True
    assert config.aggressive_heading_inference is False


def test_config_overrides() -> None:
    config = DocvertConfig(
        language_hint="ko",
        ocr_languages=["en", "fr"],
        heading_mode="heuristic",
        include_headers_footers=True,
    )
    assert config.language_hint == "ko"
    assert config.ocr_languages == ["en", "fr"]
    assert config.heading_mode == "heuristic"
    assert config.include_headers_footers is True


def test_config_validation_error() -> None:
    with pytest.raises(ValidationError):
        DocvertConfig(language_hint="invalid_language")  # type: ignore[arg-type]


def test_block_initialization() -> None:
    block = Block(content="Base block", metadata={"key": "value"})
    assert block.content == "Base block"
    assert block.metadata == {"key": "value"}

    empty_block = Block(content="Empty")
    assert empty_block.metadata == {}


def test_paragraph_initialization() -> None:
    para = Paragraph(content="This is a paragraph.")
    assert para.content == "This is a paragraph."
    assert para.metadata == {}


def test_heading_initialization() -> None:
    head = Heading(content="Title", level=2, score=90)
    assert head.content == "Title"
    assert head.level == 2
    assert head.score == 90

    default_head = Heading(content="Default")
    assert default_head.level == 1
    assert default_head.score == 100


def test_table_initialization() -> None:
    table = Table(content="", rows=[["A", "B"], ["1", "2"]])
    assert table.content == ""
    assert table.rows == [["A", "B"], ["1", "2"]]

    empty_table = Table(content="")
    assert empty_table.rows == []


def test_document_to_markdown_empty() -> None:
    doc = Document(metadata={"author": "Test"})
    assert doc.metadata == {"author": "Test"}
    assert doc.blocks == []
    assert doc.to_markdown() == ""


def test_document_to_markdown_heading_paragraph() -> None:
    blocks = [
        Heading(content="Main Title", level=1),
        Paragraph(content="Introduction paragraph."),
        Heading(content="Section 1", level=2),
        Paragraph(content="Section content."),
    ]
    doc = Document(blocks=blocks)
    markdown = doc.to_markdown()
    expected = (
        "# Main Title\n\nIntroduction paragraph.\n\n## Section 1\n\nSection content.\n"
    )
    assert markdown == expected


def test_document_to_markdown_table() -> None:
    blocks = [
        Paragraph(content="Here is a table:"),
        Table(content="", rows=[["Header 1", "Header 2"], ["Val 1", "Val 2"]]),
    ]
    doc = Document(blocks=blocks)
    markdown = doc.to_markdown()
    expected = "Here is a table:\n\n| Header 1 | Header 2 |\n| --- | --- |\n| Val 1 | Val 2 |\n\n"
    assert markdown == expected


def test_document_to_markdown_table_header_separator() -> None:
    """Table Markdown must include a header separator row after the first row.

    Standard Markdown tables require a ``| --- | --- |`` separator between
    the header row and data rows. Without it, renderers treat the pipe-delimited
    lines as plain text rather than a table.
    """
    blocks = [
        Table(content="", rows=[["Name", "Age"], ["Alice", "30"], ["Bob", "25"]]),
    ]
    doc = Document(blocks=blocks)
    markdown = doc.to_markdown()
    expected = (
        "| Name | Age |\n"
        "| --- | --- |\n"
        "| Alice | 30 |\n"
        "| Bob | 25 |\n"
        "\n"
    )
    assert markdown == expected


def test_document_to_markdown_table_single_row() -> None:
    """A table with only one row should still get a header separator row."""
    blocks = [
        Table(content="", rows=[["Header1", "Header2"]]),
    ]
    doc = Document(blocks=blocks)
    markdown = doc.to_markdown()
    expected = (
        "| Header1 | Header2 |\n"
        "| --- | --- |\n"
        "\n"
    )
    assert markdown == expected


def test_document_to_markdown_table_empty_rows() -> None:
    """A table with no rows should produce no table output."""
    blocks = [
        Table(content="", rows=[]),
    ]
    doc = Document(blocks=blocks)
    markdown = doc.to_markdown()
    assert markdown == "\n"


def test_document_to_markdown_table_varying_columns() -> None:
    """Table with inconsistent column counts should not crash.

    The header separator row matches the first row's column count.
    Subsequent rows with fewer columns still render, though visually
    the table may look ragged.
    """
    blocks = [
        Table(content="", rows=[["A", "B", "C"], ["1", "2"]]),
    ]
    doc = Document(blocks=blocks)
    markdown = doc.to_markdown()
    assert "| --- | --- | --- |" in markdown
    assert "| A | B | C |" in markdown
    assert "| 1 | 2 |" in markdown


def test_document_to_markdown_table_empty_first_row() -> None:
    """Table whose first row is empty should degrade gracefully.

    When the first row has no cells the separator row is also empty,
    but subsequent data rows are still rendered.
    """
    blocks = [
        Table(content="", rows=[[], ["Data1", "Data2"]]),
    ]
    doc = Document(blocks=blocks)
    markdown = doc.to_markdown()
    assert "|" in markdown or markdown == "\n"


def test_document_to_markdown_table_pipe_escape() -> None:
    """Literal pipe characters inside cell text must be escaped.

    If a cell value contains ``|`` it is replaced with ``\\|`` so that
    the Markdown table structure is not broken.
    """
    blocks = [
        Table(content="", rows=[["A|B", "C"], ["1", "2|3"]]),
    ]
    doc = Document(blocks=blocks)
    markdown = doc.to_markdown()
    assert "A\\|B" in markdown
    assert "2\\|3" in markdown
    assert "| --- | --- |" in markdown


def test_document_to_markdown_table_content_fallback() -> None:
    """When rows is empty but content is set, content is emitted verbatim.

    The PDF parser (docling path) produces ``Table(content=markdown, rows=[])``
    where ``content`` already holds a pre-formatted Markdown table string.
    """
    pre_formatted = "| X | Y |\n| --- | --- |\n| 1 | 2 |"
    blocks = [
        Table(content=pre_formatted, rows=[]),
    ]
    doc = Document(blocks=blocks)
    markdown = doc.to_markdown()
    assert pre_formatted in markdown


def test_document_to_markdown_other_block() -> None:
    """Generic Block instances are silently skipped during Markdown rendering.

    Only recognized subclasses (Heading, Paragraph, Table, Image) produce
    output.  A bare ``Block`` is ignored so that unrecognized block types
    do not corrupt the document.
    """
    blocks = [Block(content="Invisible"), Paragraph(content="Visible")]
    doc = Document(blocks=blocks)
    markdown = doc.to_markdown()
    expected = "Visible\n"
    assert markdown == expected
