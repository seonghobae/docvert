"""Root entrypoint for Docvert.

This script delegates to the main CLI application.
It is provided to allow running the application via `uv run main.py`.
"""

from docvert.cli.main import main as cli_main


def main() -> None:
    """Main execution function delegating to the CLI."""
    cli_main()


if __name__ == "__main__":
    main()
