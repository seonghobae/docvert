from pathlib import Path

from typing import Any
import sys
import pytest
import runpy
import importlib
from unittest.mock import patch

from docvert.cli.main import main


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Any:
    d1 = tmp_path / "dir1"
    d1.mkdir()
    f1 = d1 / "file1.txt"
    f1.write_text("dummy")

    f2 = tmp_path / "file2.txt"
    f2.write_text("dummy")

    return tmp_path, d1, f1, f2


def test_no_inputs(capsys: Any) -> None:
    with patch.object(sys, "argv", ["docvert"]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert "No command provided" in captured.err


@patch("docvert.cli.main.BatchProcessor")
def test_valid_file_inputs(mock_processor: Any, temp_workspace: Any) -> None:
    tmp_path, d1, f1, f2 = temp_workspace

    with patch.object(sys, "argv", ["docvert", "convert", str(f1)]):
        main()

    mock_processor.return_value.process.assert_called_once()
    args = mock_processor.return_value.process.call_args[0][0]
    assert len(args) == 1
    assert f1 in args


@patch("docvert.cli.main.BatchProcessor")
def test_valid_dir_input(mock_processor: Any, temp_workspace: Any) -> None:
    tmp_path, d1, f1, f2 = temp_workspace

    with patch.object(sys, "argv", ["docvert", "batch", str(d1)]):
        main()

    mock_processor.return_value.process.assert_called_once()
    args = mock_processor.return_value.process.call_args[0][0]
    assert len(args) == 1
    assert f1 in args


@patch("docvert.cli.main.BatchProcessor")
def test_batch_dir_input_nested(mock_processor: Any, temp_workspace: Any) -> None:
    tmp_path, d1, f1, f2 = temp_workspace

    with patch.object(sys, "argv", ["docvert", "batch", str(tmp_path)]):
        main()

    mock_processor.return_value.process.assert_called_once()
    args = mock_processor.return_value.process.call_args[0][0]
    assert len(args) == 2
    assert f1 in args
    assert f2 in args


def test_invalid_input_dir(capsys: Any, temp_workspace: Any) -> None:
    tmp_path, d1, f1, f2 = temp_workspace
    invalid_dir = tmp_path / "does_not_exist"

    with patch.object(sys, "argv", ["docvert", "batch", str(invalid_dir)]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert "is not a directory" in captured.err


@patch("docvert.cli.main.BatchProcessor")
def test_non_existent_positional_input(
    mock_processor: Any, capsys: Any, temp_workspace: Any
) -> None:
    tmp_path, d1, f1, f2 = temp_workspace
    invalid_file = tmp_path / "does_not_exist.txt"

    with patch.object(sys, "argv", ["docvert", "convert", str(invalid_file)]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1

    captured = capsys.readouterr()
    assert "does not exist" in captured.err


@patch("docvert.cli.main.BatchProcessor")
def test_custom_config(mock_processor: Any, temp_workspace: Any) -> None:
    tmp_path, d1, f1, f2 = temp_workspace

    custom_args = [
        "docvert",
        "convert",
        str(f1),
        "--language-hint",
        "en",
        "--ocr-languages",
        "en",
        "fr",
        "--heading-mode",
        "heuristic",
        "--no-deterministic",
        "--llm-refiner",
        "--llm-model",
        "gpt-4",
    ]

    with patch.object(sys, "argv", custom_args):
        main()

    mock_processor.assert_called_once()
    config = mock_processor.call_args[1]["config"]
    assert config.language_hint == "en"
    assert config.ocr_languages == ["en", "fr"]
    assert config.heading_mode == "heuristic"
    assert config.deterministic is False
    assert config.use_llm_refiner is True
    assert config.llm_model == "gpt-4"


def test_main_execution() -> None:
    # Temporarily remove the module from sys.modules to avoid runpy RuntimeWarning
    orig_module = sys.modules.pop("docvert.cli.main", None)
    try:
        with (
            patch.object(sys, "argv", ["docvert"]),
            pytest.raises(SystemExit) as excinfo,
        ):
            runpy.run_module("docvert.cli.main", run_name="__main__")
        assert excinfo.value.code == 1
    finally:
        if orig_module:
            sys.modules["docvert.cli.main"] = orig_module


def test_fallback_batch_processor(capsys: Any, temp_workspace: Any) -> None:
    # Force ImportError for docvert.core.batch
    import docvert.cli.main

    with patch.dict("sys.modules", {"docvert.core.batch": None}):
        importlib.reload(docvert.cli.main)

        tmp_path, d1, f1, f2 = temp_workspace
        with patch.object(sys, "argv", ["docvert", "convert", str(f1)]):
            docvert.cli.main.main()

        captured = capsys.readouterr()
        assert "Stub: Processing 1 files with config:" in captured.out

    # Reload again to restore original state
    importlib.reload(docvert.cli.main)
