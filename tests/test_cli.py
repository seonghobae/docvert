import sys
import pytest
import runpy
import importlib
from unittest.mock import patch, MagicMock
from pathlib import Path

from docvert.cli.main import main, parse_args


@pytest.fixture
def temp_workspace(tmp_path):
    d1 = tmp_path / "dir1"
    d1.mkdir()
    f1 = d1 / "file1.txt"
    f1.write_text("dummy")

    f2 = tmp_path / "file2.txt"
    f2.write_text("dummy")

    return tmp_path, d1, f1, f2


def test_no_inputs(capsys):
    with patch.object(sys, "argv", ["docvert"]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert "Error: No valid input files provided." in captured.err


@patch("docvert.cli.main.BatchProcessor")
def test_valid_file_inputs(mock_processor, temp_workspace):
    tmp_path, d1, f1, f2 = temp_workspace

    with patch.object(sys, "argv", ["docvert", str(f1), str(f2)]):
        main()

    mock_processor.return_value.process.assert_called_once()
    args = mock_processor.return_value.process.call_args[0][0]
    assert len(args) == 2
    assert f1 in args
    assert f2 in args


@patch("docvert.cli.main.BatchProcessor")
def test_valid_dir_input(mock_processor, temp_workspace):
    tmp_path, d1, f1, f2 = temp_workspace

    with patch.object(sys, "argv", ["docvert", "--input-dir", str(d1)]):
        main()

    mock_processor.return_value.process.assert_called_once()
    args = mock_processor.return_value.process.call_args[0][0]
    assert len(args) == 1
    assert f1 in args


@patch("docvert.cli.main.BatchProcessor")
def test_mixed_inputs_with_deduplication(mock_processor, temp_workspace):
    tmp_path, d1, f1, f2 = temp_workspace

    with patch.object(
        sys, "argv", ["docvert", str(f1), str(d1), "--input-dir", str(tmp_path)]
    ):
        main()

    mock_processor.return_value.process.assert_called_once()
    args = mock_processor.return_value.process.call_args[0][0]
    assert len(args) == 2
    assert f1 in args
    assert f2 in args


def test_invalid_input_dir(capsys, temp_workspace):
    tmp_path, d1, f1, f2 = temp_workspace
    invalid_dir = tmp_path / "does_not_exist"

    with patch.object(sys, "argv", ["docvert", "--input-dir", str(invalid_dir)]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert "is not a directory" in captured.err


@patch("docvert.cli.main.BatchProcessor")
def test_non_existent_positional_input(mock_processor, capsys, temp_workspace):
    tmp_path, d1, f1, f2 = temp_workspace
    invalid_file = tmp_path / "does_not_exist.txt"

    with patch.object(sys, "argv", ["docvert", str(invalid_file), str(f1)]):
        main()

    captured = capsys.readouterr()
    assert "does not exist." in captured.err
    mock_processor.return_value.process.assert_called_once()


@patch("docvert.cli.main.BatchProcessor")
def test_custom_config(mock_processor, temp_workspace):
    tmp_path, d1, f1, f2 = temp_workspace

    custom_args = [
        "docvert",
        str(f1),
        "--language-hint",
        "en",
        "--ocr-languages",
        "en",
        "fr",
        "--heading-mode",
        "heuristic",
        "--no-continue-on-error",
        "--no-deterministic",
    ]

    with patch.object(sys, "argv", custom_args):
        main()

    mock_processor.assert_called_once()
    config = mock_processor.call_args[1]["config"]
    assert config.language_hint == "en"
    assert config.ocr_languages == ["en", "fr"]
    assert config.heading_mode == "heuristic"
    assert config.continue_on_error is False
    assert config.deterministic is False


def test_main_execution():
    with patch.object(sys, "argv", ["docvert"]), pytest.raises(SystemExit) as excinfo:
        runpy.run_module("docvert.cli.main", run_name="__main__")
    assert excinfo.value.code == 1


def test_fallback_batch_processor(capsys, temp_workspace):
    # Force ImportError for docvert.core.batch
    import docvert.cli.main

    with patch.dict("sys.modules", {"docvert.core.batch": None}):
        importlib.reload(docvert.cli.main)

        tmp_path, d1, f1, f2 = temp_workspace
        with patch.object(sys, "argv", ["docvert", str(f1)]):
            docvert.cli.main.main()

        captured = capsys.readouterr()
        assert "Stub: Processing 1 files with config:" in captured.out

    # Reload again to restore original state
    importlib.reload(docvert.cli.main)
