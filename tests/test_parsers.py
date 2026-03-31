from typing import Any
from pathlib import Path
import pytest
import importlib
from unittest.mock import MagicMock, patch, mock_open

from docvert.models.document import Document, Heading, Paragraph, Table
from docvert.parsers.docx_parser import DocxParser
from docvert.parsers.pdf_parser import PdfParser

# --- DOCX Parser Tests ---


def test_docx_parser_file_not_found() -> None:
    parser = DocxParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent_file.docx")


@patch("docvert.parsers.docx_parser.docx.Document")
@patch("docvert.parsers.docx_parser.Paragraph")
def test_docx_parser_python_docx_success(
    mock_paragraph_cls: Any, mock_docx_doc: Any, tmp_path: Path
) -> None:
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
    mock_mammoth_parse: Any, mock_python_docx_parse: Any, tmp_path: Path
) -> None:
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
def test_docx_parser_parse_with_mammoth(mock_convert: Any, tmp_path: Path) -> None:
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


def test_docx_parser_heading_scoring() -> None:
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
    block_heading = parser._process_paragraph(p1)[0]
    assert isinstance(block_heading, Heading)
    assert block_heading.level == 1

    # 70-84 warning case -> regular paragraph
    block_warning = parser._process_paragraph(p4)[
        0
    ]  # score 50 (wait, recalculate p4 with run2 gave 50. Let's make it 70 again)
    p4.runs = [run1]
    block_warning = parser._process_paragraph(p4)[0]  # score 70
    assert isinstance(block_warning, Paragraph)

    # < 70 case
    p_reg = MagicMock()
    p_reg.text = "Regular"
    p_reg.style = None
    p_reg.runs = []
    block_reg = parser._process_paragraph(p_reg)[0]
    assert isinstance(block_reg, Paragraph)


# --- PDF Parser Tests ---


def test_pdf_parser_file_not_found() -> None:
    parser = PdfParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent_file.pdf")


@patch("docvert.parsers.pdf_parser.DOCLING_AVAILABLE", True)
@patch("docvert.parsers.pdf_parser.DocumentConverter")
def test_pdf_parser_docling_success(mock_converter_cls: Any, tmp_path: Path) -> None:
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    mock_converter = MagicMock()
    mock_converter_cls.return_value = mock_converter

    mock_result = MagicMock()

    class TextItem:
        def __init__(self, text: str, label: str = "text") -> None:
            self.text = text
            self.label = label

    class TableItem:
        def export_to_markdown(self) -> str:
            return "| cell |"

    class GenericItem:
        def __init__(self) -> None:
            self.text = "generic"

    def mock_iterate() -> Any:
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
def test_pdf_parser_docling_no_items_fallback(
    mock_converter_cls: Any, tmp_path: Path
) -> None:
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
def test_pdf_parser_unstructured_success(mock_partition: Any, tmp_path: Path) -> None:
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    class MockTitle:
        category = "Title"

        def __str__(self) -> str:
            return "My Title"

    class MockTable:
        category = "Table"

        def __str__(self) -> str:
            return "Table Content"

        class Metadata:
            text_as_html = "<table></table>"

        metadata = Metadata()

    class MockText:
        category = "Text"

        def __str__(self) -> str:
            return "My Text"

    class MockEmpty:
        category = "Text"

        def __str__(self) -> str:
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
def test_pdf_parser_unstructured_empty_fallback(
    mock_partition: Any, tmp_path: Path
) -> None:
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    class MockText:
        category = "Text"

        def __str__(self) -> str:
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
def test_pdf_parser_unstructured_exception_fallback(
    mock_partition: Any, tmp_path: Path
) -> None:
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    class MockText:
        category = "Text"

        def __str__(self) -> str:
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
def test_pdf_parser_both_unavailable(tmp_path: Path) -> None:
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    parser = PdfParser()
    with pytest.raises(RuntimeError, match="Both parsers failed or missing"):
        parser.parse(file_path)


@patch("docvert.parsers.pdf_parser.DOCLING_AVAILABLE", True)
@patch("docvert.parsers.pdf_parser.UNSTRUCTURED_AVAILABLE", False)
@patch("docvert.parsers.pdf_parser.PdfParser._parse_with_docling")
def test_pdf_parser_docling_fails_unstructured_unavailable(
    mock_parse_docling: Any, tmp_path: Path
) -> None:
    file_path = tmp_path / "test.pdf"
    file_path.touch()

    mock_parse_docling.side_effect = Exception("docling crash")

    parser = PdfParser()
    with pytest.raises(RuntimeError, match="Both parsers failed or missing"):
        parser.parse(file_path)


def test_pdf_parser_import_error_handling() -> None:
    # Simulate missing docling and unstructured by temporarily patching sys.modules
    import docvert.parsers.pdf_parser as pdf_parser_module

    # Save original __import__
    original_import = __builtins__["__import__"]  # type: ignore

    def mocked_import(name: str, *args: Any, **kwargs: Any) -> Any:
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


def test_pdf_parser_import_success_handling() -> None:
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


def test_docx_parser_image_extraction() -> None:
    parser = DocxParser()
    p_mock = MagicMock()
    p_mock.text = "Hello"
    p_mock.style = None
    p_mock.runs = []

    run_mock = MagicMock()
    run_mock.text = "run"
    run_mock.font.size.pt = 12

    # Mock XML drawing element
    drawing_mock = MagicMock()
    blip_mock = MagicMock()

    # Mocking attrib vs get
    def blip_get(key: str) -> str:
        if "embed" in key:
            return "rId1"
        return ""

    blip_mock.get.side_effect = blip_get

    drawing_mock.findall.return_value = [blip_mock]
    run_mock._element.findall.return_value = [drawing_mock]

    # Mock part and related_parts
    p_mock.part = MagicMock()
    related_part_mock = MagicMock()
    related_part_mock.content_type = "image/png"
    related_part_mock.blob = b"fakeimagebytes"

    p_mock.part.related_parts.get.return_value = related_part_mock
    p_mock.runs.append(run_mock)

    blocks = parser._process_paragraph(p_mock)
    assert len(blocks) == 2  # 1 Paragraph, 1 Image
    from docvert.models.document import Image

    assert isinstance(blocks[0], Paragraph)
    assert isinstance(blocks[1], Image)
    assert blocks[1].extension == ".png"
    assert blocks[1].image_bytes == b"fakeimagebytes"

    # Also test empty/fallback content types
    assert parser._get_extension_from_content_type("image/jpeg") == ".jpg"
    assert parser._get_extension_from_content_type("unknown") == ".bin"


def test_docx_parser_image_extraction_fallbacks() -> None:
    parser = DocxParser()
    p_mock = MagicMock()
    p_mock.text = "Hello fallback"
    p_mock.style = None
    p_mock.runs = []

    run_mock = MagicMock()
    run_mock.text = "run"
    run_mock.font.size.pt = 12

    drawing_mock = MagicMock()
    blip_mock = MagicMock()

    def run_findall(query: str) -> list[Any]:
        if "{" in query:
            return []
        return [drawing_mock]

    run_mock._element.findall.side_effect = run_findall

    def drawing_findall(query: str) -> list[Any]:
        if "{" in query:
            return []
        return [blip_mock]

    drawing_mock.findall.side_effect = drawing_findall

    # Force get to return None, to trigger blip.attrib
    blip_mock.get.return_value = None
    blip_mock.attrib = {"embed": "rIdFallback"}

    p_mock.part = MagicMock()
    related_part_mock = MagicMock()
    related_part_mock.content_type = "image/png"
    related_part_mock.blob = b"fallbackbytes"

    p_mock.part.related_parts.get.return_value = related_part_mock
    p_mock.runs.append(run_mock)

    blocks = parser._process_paragraph(p_mock)
    assert len(blocks) == 2
    from docvert.models.document import Image

    assert isinstance(blocks[1], Image)
    assert blocks[1].image_bytes == b"fallbackbytes"
    assert blocks[1].extension == ".png"


def test_pdf_parser_docling_image_extraction(tmp_path: Path) -> None:
    file_path = tmp_path / "dummy.pdf"
    file_path.touch()
    from docvert.parsers.pdf_parser import PdfParser
    from docvert.models.document import Image

    parser = PdfParser()

    class PictureItem:
        def __init__(self, raise_error: bool = False) -> None:
            self.text = "alt text"
            self.raise_error = raise_error

        def get_image(self, doc: Any) -> Any:
            if self.raise_error:
                raise RuntimeError("mock error")
            img = MagicMock()
            img.format = "JPEG"

            def save_mock(buf: Any, format: str) -> None:
                buf.write(b"fakejpeg")

            img.save = save_mock
            return img

    mock_result = MagicMock()

    def mock_iterate() -> Any:
        yield PictureItem(), 1
        yield PictureItem(raise_error=True), 2

    mock_result.document.iterate_items = mock_iterate

    with patch("docvert.parsers.pdf_parser.DOCLING_AVAILABLE", True):
        with patch(
            "docvert.parsers.pdf_parser.DocumentConverter"
        ) as mock_converter_cls:
            mock_converter_cls.return_value.convert.return_value = mock_result
            doc = parser.parse(file_path)
            assert len(doc.blocks) == 1
            assert isinstance(doc.blocks[0], Image)
            assert doc.blocks[0].extension == ".jpeg"
            assert doc.blocks[0].image_bytes == b"fakejpeg"
            assert doc.blocks[0].alt_text == "alt text"


def test_pdf_parser_unstructured_image_extraction(tmp_path: Path) -> None:
    file_path = tmp_path / "dummy.pdf"
    file_path.touch()
    from docvert.parsers.pdf_parser import PdfParser
    from docvert.models.document import Image, Paragraph
    import base64

    parser = PdfParser()

    class MockImage:
        category = "Image"

        def __init__(self, has_base64: bool = True) -> None:
            self.metadata = MagicMock()
            if has_base64:
                self.metadata.image_base64 = base64.b64encode(b"fakeunstruct").decode(
                    "utf-8"
                )
                self.metadata.image_mime_type = "image/png"
            else:
                self.metadata.image_base64 = None

        def __str__(self) -> str:
            return "img text"

    with patch("docvert.parsers.pdf_parser.DOCLING_AVAILABLE", False):
        with patch("docvert.parsers.pdf_parser.UNSTRUCTURED_AVAILABLE", True):
            with patch("docvert.parsers.pdf_parser.partition_pdf") as mock_partition:
                # First one with base64, second without
                mock_partition.return_value = [MockImage(True), MockImage(False)]
                doc = parser.parse(file_path)
                assert len(doc.blocks) == 2
                assert isinstance(doc.blocks[0], Image)
                assert doc.blocks[0].image_bytes == b"fakeunstruct"
                assert doc.blocks[0].extension == ".png"
                # The second one without base64 falls back to Paragraph
                assert isinstance(doc.blocks[1], Paragraph)
                assert doc.blocks[1].content == "img text"
