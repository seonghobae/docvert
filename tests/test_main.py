"""Tests for the root main module."""

import runpy
from unittest.mock import patch

from main import main


def test_root_main_execution() -> None:
    """Test that root main.py delegates to docvert.cli.main.main."""
    with patch("main.cli_main") as mock_cli_main:
        main()
        mock_cli_main.assert_called_once()


def test_main_as_script() -> None:
    """Test execution when run as a script."""
    with patch("docvert.cli.main.main") as mock_cli_main:
        runpy.run_module("main", run_name="__main__")
        mock_cli_main.assert_called_once()
