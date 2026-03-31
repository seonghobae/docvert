import json
import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from docvert.models.config import DocvertConfig
from docvert.models.document import Document
from docvert.core.writer import Writer
from docvert.core.batch import BatchProcessor, calculate_md5

# --- tests for writer.py ---


def test_writer_init(tmp_path):
    """Test that Writer creates the output directory upon initialization."""
    output_dir = tmp_path / "out"
    Writer(output_dir)
    assert output_dir.exists()


def test_writer_write_markdown(tmp_path):
    writer = Writer(tmp_path)
    doc = MagicMock(spec=Document)
    doc.to_markdown.return_value = "# Markdown Content"

    out_path = writer.write_markdown(doc, "test_file")
    assert out_path == tmp_path / "test_file.md"
    assert out_path.read_text(encoding="utf-8") == "# Markdown Content"


def test_writer_write_json_sidecar(tmp_path):
    writer = Writer(tmp_path)
    meta = {"key": "value"}
    out_path = writer.write_json_sidecar(meta, "test_file")
    assert out_path == tmp_path / "test_file.conversion.json"
    with open(out_path, "r", encoding="utf-8") as f:
        assert json.load(f) == meta


def test_writer_create_assets_dir(tmp_path):
    writer = Writer(tmp_path)
    assets_dir = writer.create_assets_dir("test_file")
    assert assets_dir == tmp_path / "test_file.assets"
    assert assets_dir.exists()
    assert assets_dir.is_dir()


def test_writer_write_batch_summary(tmp_path):
    writer = Writer(tmp_path)
    summaries = [{"a": 1}, {"b": 2}]
    out_path = writer.write_batch_summary(summaries)
    assert out_path == tmp_path / "batch-summary.jsonl"
    lines = out_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"a": 1}
    assert json.loads(lines[1]) == {"b": 2}


def test_writer_write_csv(tmp_path):
    writer = Writer(tmp_path)

    # Empty list should not create a file
    out_path = writer.write_csv("test.csv", ["col1", "col2"], [])
    assert out_path == tmp_path / "test.csv"
    assert not out_path.exists()

    # Non-empty list should create a file
    rows = [{"col1": "A", "col2": "B"}]
    out_path = writer.write_csv("test.csv", ["col1", "col2"], rows)
    assert out_path.exists()
    text = out_path.read_text(encoding="utf-8")
    assert "col1,col2" in text
    assert "A,B" in text


# --- tests for batch.py ---


def test_calculate_md5(tmp_path):
    f = tmp_path / "file.txt"
    content = b"hello world"
    f.write_bytes(content)

    expected = hashlib.md5(content).hexdigest()
    assert calculate_md5(f) == expected


def test_batch_processor_init_default_dir():
    config = DocvertConfig()
    with patch("docvert.core.batch.Path.cwd") as mock_cwd:
        mock_cwd.return_value = Path("/tmp/cwd")
        bp = BatchProcessor(config)
        assert bp.output_dir == Path("/tmp/cwd")


def test_batch_processor_init_custom_dir(tmp_path):
    config = DocvertConfig()
    bp = BatchProcessor(config, output_dir=tmp_path)
    assert bp.output_dir == tmp_path


@patch("docvert.core.batch.DocxParser")
@patch("docvert.core.batch.PdfParser")
def test_batch_processor_process_file_docx(MockPdfParser, MockDocxParser, tmp_path):
    config = DocvertConfig(cache_by_hash=False)
    bp = BatchProcessor(config, output_dir=tmp_path)

    mock_parser = MockDocxParser.return_value
    mock_doc = MagicMock()
    mock_doc.metadata = {"warnings": ["w1"], "confidence": 0.9}
    mock_doc.to_markdown.return_value = "content"
    mock_parser.parse.return_value = mock_doc

    in_file = tmp_path / "doc.docx"
    in_file.write_bytes(b"dummy")

    res = bp.process_file(in_file)

    assert res["input_format"] == ".docx"
    assert res["warnings"] == ["w1"]
    assert res["confidence"] == 0.9
    assert res["source_file"] == str(in_file)
    assert "parser_path_used" in res


@patch("docvert.core.batch.DocxParser")
@patch("docvert.core.batch.PdfParser")
def test_batch_processor_process_file_pdf(MockPdfParser, MockDocxParser, tmp_path):
    config = DocvertConfig(cache_by_hash=False)
    bp = BatchProcessor(config, output_dir=tmp_path)

    mock_parser = MockPdfParser.return_value
    mock_doc = MagicMock()
    mock_doc.metadata = {}
    mock_doc.to_markdown.return_value = "content"
    mock_parser.parse.return_value = mock_doc

    in_file = tmp_path / "doc.pdf"
    in_file.write_bytes(b"dummy")

    res = bp.process_file(in_file)
    assert res["input_format"] == ".pdf"


def test_batch_processor_process_file_unsupported(tmp_path):
    config = DocvertConfig()
    bp = BatchProcessor(config, output_dir=tmp_path)

    in_file = tmp_path / "doc.txt"
    in_file.write_text("hello")

    with pytest.raises(ValueError, match="Unsupported file extension: .txt"):
        bp.process_file(in_file)


def test_batch_processor_process_file_cache_hit(tmp_path):
    config = DocvertConfig(cache_by_hash=True)
    bp = BatchProcessor(config, output_dir=tmp_path)

    in_file = tmp_path / "doc.docx"
    content = b"cache me"
    in_file.write_bytes(content)
    file_hash = hashlib.md5(content).hexdigest()

    # Create mock cache files
    json_path = tmp_path / "doc.conversion.json"
    cached_meta = {"file_hash": file_hash, "cached": True}
    json_path.write_text(json.dumps(cached_meta))

    md_path = tmp_path / "doc.md"
    md_path.write_text("markdown")

    res = bp.process_file(in_file)
    assert res == cached_meta


def test_batch_processor_process_file_cache_miss_no_md(tmp_path):
    config = DocvertConfig(cache_by_hash=True)
    bp = BatchProcessor(config, output_dir=tmp_path)

    in_file = tmp_path / "doc.docx"
    content = b"dummy"
    in_file.write_bytes(content)
    file_hash = hashlib.md5(content).hexdigest()

    # Cache json exists but md doesn't
    json_path = tmp_path / "doc.conversion.json"
    cached_meta = {"file_hash": file_hash}
    json_path.write_text(json.dumps(cached_meta))

    with patch.object(bp, "docx_parser") as mock_parser:
        mock_doc = MagicMock()
        mock_doc.metadata = {}
        mock_doc.to_markdown.return_value = "content"
        mock_parser.parse.return_value = mock_doc

        res = bp.process_file(in_file)
        assert res["input_format"] == ".docx"


def test_batch_processor_process_file_cache_miss_wrong_hash(tmp_path):
    config = DocvertConfig(cache_by_hash=True)
    bp = BatchProcessor(config, output_dir=tmp_path)

    in_file = tmp_path / "doc.docx"
    content = b"dummy"
    in_file.write_bytes(content)

    # Cache json exists but hash doesn't match
    json_path = tmp_path / "doc.conversion.json"
    cached_meta = {"file_hash": "wrong_hash"}
    json_path.write_text(json.dumps(cached_meta))

    with patch.object(bp, "docx_parser") as mock_parser:
        mock_doc = MagicMock()
        mock_doc.metadata = {}
        mock_doc.to_markdown.return_value = "content"
        mock_parser.parse.return_value = mock_doc

        res = bp.process_file(in_file)
        assert res["input_format"] == ".docx"


def test_batch_processor_process_file_cache_invalid_json(tmp_path):
    config = DocvertConfig(cache_by_hash=True)
    bp = BatchProcessor(config, output_dir=tmp_path)

    in_file = tmp_path / "doc.docx"
    in_file.write_bytes(b"dummy")

    # Invalid JSON
    json_path = tmp_path / "doc.conversion.json"
    json_path.write_text("{invalid")

    with patch.object(bp, "docx_parser") as mock_parser:
        mock_doc = MagicMock()
        mock_doc.metadata = {}
        mock_doc.to_markdown.return_value = "content"
        mock_parser.parse.return_value = mock_doc

        # Should ignore invalid JSON and proceed
        res = bp.process_file(in_file)
        assert res["input_format"] == ".docx"


def test_batch_processor_process_success_no_warnings(tmp_path):
    config = DocvertConfig()
    bp = BatchProcessor(config, output_dir=tmp_path)

    file1 = tmp_path / "file1.docx"
    file1.touch()

    with patch.object(bp, "process_file") as mock_pf:
        mock_pf.side_effect = [{"warnings": [], "source_file": "file1.docx"}]

        with (
            patch.object(bp.writer, "write_batch_summary") as mock_wbs,
            patch.object(bp.writer, "write_csv") as mock_wcsv,
        ):
            bp.process([file1])

            mock_wbs.assert_called_once()
            # warnings.csv shouldn't be written because there are no warnings
            # failures.csv shouldn't be written because there are no failures
            mock_wcsv.assert_not_called()


def test_batch_processor_process_success_with_warnings(tmp_path):
    config = DocvertConfig()
    bp = BatchProcessor(config, output_dir=tmp_path)

    file1 = tmp_path / "file1.docx"
    file2 = tmp_path / "file2.docx"
    file1.touch()
    file2.touch()

    with patch.object(bp, "process_file") as mock_pf:
        mock_pf.side_effect = [
            {"warnings": ["w1"], "source_file": "file1.docx"},
            {"warnings": [], "source_file": "file2.docx"},
        ]

        with (
            patch.object(bp.writer, "write_batch_summary") as mock_wbs,
            patch.object(bp.writer, "write_csv") as mock_wcsv,
        ):
            bp.process([file1, file2])

            mock_wbs.assert_called_once()
            # warnings.csv should be written
            mock_wcsv.assert_called_once()
            assert mock_wcsv.call_args[0][0] == "warnings.csv"


def test_batch_processor_process_failure_continue(tmp_path):
    config = DocvertConfig(continue_on_error=True)
    bp = BatchProcessor(config, output_dir=tmp_path)

    file1 = tmp_path / "file1.docx"
    file1.touch()

    with patch.object(bp, "process_file") as mock_pf:
        mock_pf.side_effect = Exception("Boom")

        with patch.object(bp.writer, "write_csv") as mock_wcsv:
            bp.process([file1])

            mock_wcsv.assert_called_once()
            assert mock_wcsv.call_args[0][0] == "failures.csv"


def test_batch_processor_process_failure_halt(tmp_path):
    config = DocvertConfig(continue_on_error=False)
    bp = BatchProcessor(config, output_dir=tmp_path)

    file1 = tmp_path / "file1.docx"
    file1.touch()

    with patch.object(bp, "process_file") as mock_pf:
        mock_pf.side_effect = Exception("Boom")

        with pytest.raises(Exception, match="Boom"):
            bp.process([file1])


def test_writer_write_markdown_string(tmp_path):
    """Test that Writer correctly writes a raw markdown string to a file."""
    writer = Writer(tmp_path)
    out_path = writer.write_markdown_string("# Refined Content", "test_file_ref")
    assert out_path == tmp_path / "test_file_ref.md"
    assert out_path.read_text(encoding="utf-8") == "# Refined Content"


@patch("docvert.core.batch.DocxParser")
@patch("docvert.core.batch.LLMRefiner")
def test_batch_processor_process_file_with_llm_refiner(
    MockLLMRefiner, MockDocxParser, tmp_path
):
    """Test that BatchProcessor uses LLMRefiner when configured to do so."""
    mock_refiner_instance = MagicMock()
    mock_refiner_instance.refine_markdown.return_value = "Refined Content"
    MockLLMRefiner.return_value = mock_refiner_instance

    mock_parser = MockDocxParser.return_value

    class FakeDoc:
        def __init__(self):
            self.metadata = {}

        def to_markdown(self):
            return "Raw Content"

    doc = FakeDoc()
    mock_parser.parse.return_value = doc

    test_file = tmp_path / "test.docx"
    test_file.touch()

    config = DocvertConfig(
        input_dir=tmp_path, output_dir=tmp_path, use_llm_refiner=True
    )
    processor = BatchProcessor(config, output_dir=tmp_path)

    result = processor.process_file(test_file)

    # check success implicitly via the result keys
    assert result["llm_refined"] is True
    MockLLMRefiner.assert_called_once()
    mock_refiner_instance.refine_markdown.assert_called_once_with("Raw Content")

    output_file = tmp_path / "test.md"
    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == "Refined Content"


@patch("docvert.core.batch.DocxParser")
@patch.dict("sys.modules", {"docvert.agent.refiner": None})
def test_batch_processor_process_file_with_llm_refiner_import_error(
    MockDocxParser, tmp_path
):
    """Test that BatchProcessor falls back gracefully if LLMRefiner is unavailable."""
    # Testing the ImportError fallback
    # We must reload the module to trigger the except ImportError block
    import importlib
    import docvert.core.batch

    importlib.reload(docvert.core.batch)

    # Re-apply the patch because we just reloaded the module
    patcher = patch("docvert.core.batch.DocxParser")
    MockDocxParser2 = patcher.start()
    mock_parser = MockDocxParser2.return_value

    class FakeDoc:
        def __init__(self):
            self.metadata = {}

        def to_markdown(self):
            return "Raw Content"

    doc = FakeDoc()
    mock_parser.parse.return_value = doc

    test_file = tmp_path / "test.docx"
    test_file.touch()

    config = DocvertConfig(
        input_dir=tmp_path, output_dir=tmp_path, use_llm_refiner=True
    )
    processor = docvert.core.batch.BatchProcessor(config, output_dir=tmp_path)

    result = processor.process_file(test_file)

    # check success implicitly via the result keys
    # Should fall back to standard writing
    assert result["llm_refined"] is False

    output_file = tmp_path / "test.md"
    assert output_file.exists()

    # Restore the module state
    importlib.reload(docvert.core.batch)
    patcher.stop()
