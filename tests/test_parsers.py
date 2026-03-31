import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

from docvert.models.document import Document, Heading, Paragraph, Table
from docvert.parsers.docx_parser import DocxParser, DocvertConfig
from docvert.parsers.pdf_parser import PdfParser

# --- DOCX Parser Tests ---


def test_docx_parser_file_not_found():
    parser = DocxParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent_file.docx")


@patch("docvert.parsers.docx_parser.docx.Document")
@patch("docvert.parsers.docx_parser.Paragraph")
def test_docx_parser_python_docx_success(mock_paragraph_cls, mock_docx_doc, tmp_path):
    # Create a dummy class to represent CT_P
    class DummyCT_P:
        pass

    with patch("docvert.parsers.docx_parser.CT_P", DummyCT_P):
        # Setup mock file
        file_path = tmp_path / "test.docx"
        file_path.touch()

        # Mock the returned document
        mock_doc = MagicMock()
        mock_docx_doc.return_value = mock_doc

        # Setup elements in the document body
        mock_p_element = DummyCT_P()
        mock_empty_p_element = DummyCT_P()

        mock_tbl_element = MagicMock()
        mock_tbl_element.tag = "w:tbl"

        mock_doc.element.body = [mock_p_element, mock_empty_p_element, mock_tbl_element]

        # Setup the wrapped paragraph mock
        mock_p = MagicMock()
        mock_p.text = "Hello World"
        mock_p.style.name = "Normal"
        mock_p.style.paragraph_format.outline_level = 9
        mock_p.runs = []

        mock_empty_p = MagicMock()
        mock_empty_p.text = "   \n"

        # mock_paragraph_cls.return_value returns the mocked paragraphs in sequence
        mock_paragraph_cls.side_effect = [mock_p, mock_empty_p]

        # Setup the table mock
        mock_table = MagicMock()
        mock_table._element = mock_tbl_element
        mock_row = MagicMock()
        mock_cell = MagicMock()
        mock_cell.text = "Cell\nData"
        mock_row.cells = [mock_cell]
        mock_table.rows = [mock_row]
        mock_doc.tables = [mock_table]

        parser = DocxParser()
        doc = parser.parse(file_path)

        assert isinstance(doc, Document)
        assert len(doc.blocks) == 2
        assert isinstance(doc.blocks[0], Paragraph)
        assert doc.blocks[0].content == "Hello World"
        assert isinstance(doc.blocks[1], Table)
        assert doc.blocks[1].rows == [["Cell Data"]]


@patch("docvert.parsers.docx_parser.DocxParser._parse_with_python_docx")
@patch("docvert.parsers.docx_parser.DocxParser._parse_with_mammoth")
def test_docx_parser_fallback_to_mammoth(
    mock_mammoth_parse, mock_python_docx_parse, tmp_path
):
    file_path = tmp_path / "test.docx"
    file_path.touch()

    mock_python_docx_parse.side_effect = Exception("docx failed")
    mock_fallback_doc = Document()
    mock_mammoth_parse.return_value = mock_fallback_doc

    parser = DocxParser()
    doc = parser.parse(file_path)

    assert doc is mock_fallback_doc
    mock_python_docx_parse.assert_called_once_with(file_path)
    mock_mammoth_parse.assert_called_once_with(file_path)


@patch("docvert.parsers.docx_parser.mammoth.convert_to_markdown")
def test_docx_parser_parse_with_mammoth(mock_convert, tmp_path):
    file_path = tmp_path / "test.docx"
    file_path.touch()

    mock_result = MagicMock()
    mock_result.value = "\n\n# Heading 1\n\nSome paragraph text\n\n"
    mock_convert.return_value = mock_result

    parser = DocxParser()
    with patch("builtins.open", mock_open()):
        doc = parser._parse_with_mammoth(file_path)

    assert len(doc.blocks) == 2
    assert isinstance(doc.blocks[0], Heading)
    assert doc.blocks[0].content == "Heading 1"
    assert doc.blocks[0].level == 1
    assert isinstance(doc.blocks[1], Paragraph)
    assert doc.blocks[1].content == "Some paragraph text"


def test_docx_parser_heading_scoring():
    parser = DocxParser()

    # 1. Built-in style: Heading 1
    p1 = MagicMock()
    p1.text = "Title"
    p1.style.name = "Heading 1"
    p1.style.paragraph_format.outline_level = 0
    p1.runs = []
    score, level = parser._calculate_heading_score(p1)
    assert score == 100  # Capped at 100
    assert level == 1

    # 2. Built-in style with invalid int
    p2 = MagicMock()
    p2.text = "Title"
    p2.style.name = "Heading X"
    p2.style.paragraph_format.outline_level = None
    p2.runs = []
    score, level = parser._calculate_heading_score(p2)
    assert score == 90
    assert level == 1

    # 3. Outline level only
    p3 = MagicMock()
    p3.text = "Title"
    p3.style.name = "Normal"
    p3.style.paragraph_format.outline_level = 2
    p3.runs = []
    score, level = parser._calculate_heading_score(p3)
    assert score == 50
    assert level == 3

    # 4. Bold and size formatting
    p4 = MagicMock()
    p4.text = "Title"
    p4.style.name = "Normal"
    del p4.style.paragraph_format

    run1 = MagicMock()
    run1.text = "BoldText"
    run1.bold = True
    run1.font.size.pt = 15
    p4.runs = [run1]

    score, level = parser._calculate_heading_score(p4)
    # bold (+30), size >= 14 (+40) -> 70
    assert score == 70

    run2 = MagicMock()
    run2.text = "BoldText"
    run2.bold = True
    run2.font.size.pt = 13
    p4.runs = [run2]
    score, level = parser._calculate_heading_score(p4)
    # bold (+30), size >= 12 (+20) -> 50
    assert score == 50

    # Test processing paragraph outputs
    block_heading = parser._process_paragraph(p1)
    assert isinstance(block_heading, Heading)
    assert block_heading.level == 1

    # 70-84 warning case -> regular paragraph
    block_warning = parser._process_paragraph(
        p4
    )  # score 50 (wait, recalculate p4 with run2 gave 50. Let's make it 70 again)
    p4.runs = [run1]
    block_warning = parser._process_paragraph(p4)  # score 70
    assert isinstance(block_warning, Paragraph)

    # < 70 case
    p_reg = MagicMock()
    p_reg.text = "Regular"
    p_reg.style = None
    p_reg.runs = []
    block_reg = parser._process_paragraph(p_reg)
    assert isinstance(block_reg, Paragraph)


# --- PDF Parser Tests ---


def test_pdf_parser_file_not_found():
    parser = PdfParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent_file.pdf")


@patch("docvert.parsers.pdf_parser.DOCLING_AVAILABLE", True)
@patch("docvert.parsers.pdf_parser.DocumentConverter")
def test_pdf_parser_docling_success(mock_converter_cls, tmp_path):
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    mock_converter = MagicMock()
    mock_converter_cls.return_value = mock_converter

    mock_result = MagicMock()

    class TextItem:
        def __init__(self, text, label="text"):
            self.text = text
            self.label = label

    class TableItem:
        def export_to_markdown(self):
            return "| cell |"

    class GenericItem:
        def __init__(self):
            self.text = "generic"

    def mock_iterate():
        yield TextItem("Title Text", "title"), 1
        yield TextItem("Body Text"), 1
        yield TableItem(), 1
        yield GenericItem(), 1

    mock_result.document.iterate_items = mock_iterate
    mock_converter.convert.return_value = mock_result

    parser = PdfParser()
    doc = parser.parse(file_path)

    assert len(doc.blocks) == 4
    assert isinstance(doc.blocks[0], Heading)
    assert doc.blocks[0].content == "Title Text"
    assert isinstance(doc.blocks[1], Paragraph)
    assert doc.blocks[1].content == "Body Text"
    assert isinstance(doc.blocks[2], Table)
    assert doc.blocks[2].content == "| cell |"
    assert isinstance(doc.blocks[3], Paragraph)
    assert doc.blocks[3].content == "generic"


@patch("docvert.parsers.pdf_parser.DOCLING_AVAILABLE", True)
@patch("docvert.parsers.pdf_parser.DocumentConverter")
def test_pdf_parser_docling_no_items_fallback(mock_converter_cls, tmp_path):
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    mock_converter = MagicMock()
    mock_converter_cls.return_value = mock_converter

    mock_result = MagicMock()
    # Mock empty iteration to trigger ValueError
    mock_result.document.iterate_items = lambda: iter([])
    mock_result.document.export_to_markdown.return_value = "Fallback markdown"
    mock_converter.convert.return_value = mock_result

    parser = PdfParser()
    doc = parser.parse(file_path)

    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], Paragraph)
    assert doc.blocks[0].content == "Fallback markdown"


@patch("docvert.parsers.pdf_parser.DOCLING_AVAILABLE", False)
@patch("docvert.parsers.pdf_parser.UNSTRUCTURED_AVAILABLE", True)
@patch("docvert.parsers.pdf_parser.partition_pdf", create=True)
def test_pdf_parser_unstructured_success(mock_partition, tmp_path):
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    class MockTitle:
        category = "Title"

        def __str__(self):
            return "My Title"

    class MockTable:
        category = "Table"

        def __str__(self):
            return "Table Content"

        class Metadata:
            text_as_html = "<table></table>"

        metadata = Metadata()

    class MockText:
        category = "Text"

        def __str__(self):
            return "My Text"

    class MockEmpty:
        category = "Text"

        def __str__(self):
            return "  "

    mock_partition.return_value = [MockTitle(), MockTable(), MockText(), MockEmpty()]

    parser = PdfParser()
    doc = parser.parse(file_path)

    assert len(doc.blocks) == 3
    assert isinstance(doc.blocks[0], Heading)
    assert doc.blocks[0].content == "My Title"
    assert isinstance(doc.blocks[1], Table)
    assert doc.blocks[1].metadata["text_as_html"] == "<table></table>"
    assert isinstance(doc.blocks[2], Paragraph)


@patch("docvert.parsers.pdf_parser.DOCLING_AVAILABLE", False)
@patch("docvert.parsers.pdf_parser.UNSTRUCTURED_AVAILABLE", True)
@patch("docvert.parsers.pdf_parser.partition_pdf", create=True)
def test_pdf_parser_unstructured_empty_fallback(mock_partition, tmp_path):
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    class MockText:
        category = "Text"

        def __str__(self):
            return "OCR Text"

    # First call returns empty, second returns mock text
    mock_partition.side_effect = [[], [MockText()]]

    parser = PdfParser()
    doc = parser.parse(file_path)

    assert len(doc.blocks) == 1
    assert doc.blocks[0].content == "OCR Text"
    assert mock_partition.call_count == 2


@patch("docvert.parsers.pdf_parser.DOCLING_AVAILABLE", False)
@patch("docvert.parsers.pdf_parser.UNSTRUCTURED_AVAILABLE", True)
@patch("docvert.parsers.pdf_parser.partition_pdf", create=True)
def test_pdf_parser_unstructured_exception_fallback(mock_partition, tmp_path):
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    class MockText:
        category = "Text"

        def __str__(self):
            return "OCR Exception Text"

    # First call throws exception, second returns mock text
    mock_partition.side_effect = [Exception("auto failed"), [MockText()]]

    parser = PdfParser()
    doc = parser.parse(file_path)

    assert len(doc.blocks) == 1
    assert doc.blocks[0].content == "OCR Exception Text"
    assert mock_partition.call_count == 2


@patch("docvert.parsers.pdf_parser.DOCLING_AVAILABLE", False)
@patch("docvert.parsers.pdf_parser.UNSTRUCTURED_AVAILABLE", False)
def test_pdf_parser_both_unavailable(tmp_path):
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    parser = PdfParser()
    with pytest.raises(RuntimeError, match="Both parsers failed or missing"):
        parser.parse(file_path)


@patch("docvert.parsers.pdf_parser.DOCLING_AVAILABLE", True)
@patch("docvert.parsers.pdf_parser.UNSTRUCTURED_AVAILABLE", False)
@patch("docvert.parsers.pdf_parser.PdfParser._parse_with_docling")
def test_pdf_parser_docling_fails_unstructured_unavailable(
    mock_parse_docling, tmp_path
):
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    mock_parse_docling.side_effect = Exception("docling crash")

    parser = PdfParser()
    with pytest.raises(RuntimeError, match="Both parsers failed or missing"):
        parser.parse(file_path)


import sys
import importlib


def test_pdf_parser_import_error_handling():
    # Simulate missing docling and unstructured by temporarily patching sys.modules
    import docvert.parsers.pdf_parser as pdf_parser_module

    # Save original __import__
    original_import = __builtins__["__import__"]

    def mocked_import(name, *args, **kwargs):
        if name in ("docling.document_converter", "unstructured.partition.pdf"):
            raise ImportError(f"Mocked missing {name}")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mocked_import):
        # Reload the module to trigger module-level try-except
        importlib.reload(pdf_parser_module)

    assert pdf_parser_module.DOCLING_AVAILABLE is False
    assert pdf_parser_module.UNSTRUCTURED_AVAILABLE is False

    # Restore the module state so subsequent tests or usages are not broken
    importlib.reload(pdf_parser_module)


def test_pdf_parser_import_success_handling():
    import sys
    import importlib
    import docvert.parsers.pdf_parser as pdf_parser_module

    mock_docling = MagicMock()
    mock_unstructured = MagicMock()

    with patch.dict(
        "sys.modules",
        {
            "docling.document_converter": mock_docling,
            "unstructured.partition.pdf": mock_unstructured,
        },
    ):
        importlib.reload(pdf_parser_module)

    assert pdf_parser_module.DOCLING_AVAILABLE is True
    assert pdf_parser_module.UNSTRUCTURED_AVAILABLE is True

    # Reload again to restore
    importlib.reload(pdf_parser_module)
