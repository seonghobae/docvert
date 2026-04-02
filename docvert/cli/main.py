"""Command-line interface module for Docvert."""

import argparse
import sys
from pathlib import Path
from typing import List

from docvert import __version__
from docvert.models.config import DocvertConfig
from docvert.core.batch import BatchProcessor


def parse_args() -> argparse.Namespace:
    """Parses command line arguments for the Docvert CLI.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Docvert: Convert documents to Markdown."
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"docvert {__version__}",
    )

    common_parser = argparse.ArgumentParser(add_help=False)

    common_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./out"),
        help="Directory to save the generated files. (Default: ./out)",
    )
    common_parser.add_argument(
        "--llm-refiner",
        action="store_true",
        help="Flag to use LLM to refine the markdown output.",
    )
    common_parser.add_argument(
        "--llm-model",
        type=str,
        default="gpt-4o-mini",
        help="The LLM model to use for refinement (default: gpt-4o-mini).",
    )

    # Config arguments
    common_parser.add_argument(
        "--language-hint", choices=["ko", "en", "auto"], default="auto"
    )
    common_parser.add_argument(
        "--ocr-languages",
        nargs="+",
        default=["ko", "en"],
        help="List of OCR languages (e.g., ko en)",
    )
    common_parser.add_argument(
        "--heading-mode", choices=["auto", "style_only", "heuristic"], default="auto"
    )
    common_parser.add_argument(
        "--comment-mode",
        choices=["preserve", "appendix", "inline", "drop"],
        default="preserve",
    )
    common_parser.add_argument(
        "--footnote-mode",
        choices=["preserve", "appendix", "inline"],
        default="preserve",
    )
    common_parser.add_argument(
        "--image-mode",
        choices=["extract_link", "embed", "extract_with_ocr", "skip"],
        default="extract_link",
    )
    common_parser.add_argument(
        "--table-mode",
        choices=["markdown_preferred", "html_for_complex"],
        default="markdown_preferred",
    )
    common_parser.add_argument(
        "--pdf-reading-order-mode",
        choices=["auto", "layout_strict", "ocr_fallback"],
        default="auto",
    )

    # Boolean flags
    common_parser.add_argument(
        "--include-headers-footers",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    common_parser.add_argument(
        "--normalize-heading-levels",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    common_parser.add_argument(
        "--preserve-numbering", action=argparse.BooleanOptionalAction, default=True
    )
    common_parser.add_argument(
        "--deterministic", action=argparse.BooleanOptionalAction, default=True
    )
    common_parser.add_argument(
        "--aggressive-heading-inference",
        action=argparse.BooleanOptionalAction,
        default=False,
    )

    subparsers = parser.add_subparsers(dest="command")

    # convert subcommand
    convert_parser = subparsers.add_parser(
        "convert",
        parents=[common_parser],
        help="Convert a single DOCX or PDF file to Markdown.",
    )
    convert_parser.add_argument(
        "input", type=Path, help="Path to the input DOCX or PDF file."
    )

    # batch subcommand
    batch_parser = subparsers.add_parser(
        "batch",
        parents=[common_parser],
        help="Process a directory of DOCX and/or PDF files.",
    )
    batch_parser.add_argument(
        "input_dir", type=Path, help="Path to the directory containing input files."
    )
    batch_parser.add_argument(
        "--continue-on-error", action=argparse.BooleanOptionalAction, default=True
    )
    batch_parser.add_argument(
        "--cache",
        action="store_true",
        help="Use hashing to skip already processed files.",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point for the Docvert command line interface.

    Orchestrates the full CLI workflow:

    1. Parses command-line arguments via ``parse_args()``.
    2. Resolves input files based on the chosen subcommand:
       - ``convert``: validates the single input file exists.
       - ``batch``: recursively collects all files from the input directory.
    3. Deduplicates files by resolved path while preserving order.
    4. Builds a ``DocvertConfig`` from parsed arguments, adjusting
       ``continue_on_error`` (disabled for single-file convert) and
       ``cache_by_hash`` (only enabled for batch with ``--cache``).
    5. Instantiates ``BatchProcessor`` and runs conversion.

    Side effects:
        Calls ``sys.exit(1)`` if no command is given, the input directory
        does not exist, or no valid input files are found. Writes converted
        files, sidecar JSON, and batch summary/CSV reports to ``--output-dir``.
    """
    args = parse_args()

    target_files: List[Path] = []

    if getattr(args, "command", None) == "convert":
        if args.input.is_file():
            target_files.append(args.input)
        else:
            print(
                f"Warning: '{args.input}' does not exist or is not a file.",
                file=sys.stderr,
            )

    elif getattr(args, "command", None) == "batch":
        if not args.input_dir.is_dir():
            print(f"Error: '{args.input_dir}' is not a directory.", file=sys.stderr)
            sys.exit(1)
        target_files.extend(f for f in args.input_dir.rglob("*") if f.is_file())

    else:
        print("Error: No command provided. Use 'convert' or 'batch'.", file=sys.stderr)
        sys.exit(1)

    # Deduplicate files while maintaining order
    seen = set()
    unique_target_files = []
    for f in target_files:
        if f.resolve() not in seen:
            seen.add(f.resolve())
            unique_target_files.append(f)

    if not unique_target_files:
        print("Error: No valid input files provided.", file=sys.stderr)
        sys.exit(1)

    # Prepare specific configs based on command
    continue_on_error = getattr(args, "continue_on_error", True)
    if getattr(args, "command", None) == "convert":
        continue_on_error = False

    cache_by_hash = (
        getattr(args, "cache", False)
        if getattr(args, "command", None) == "batch"
        else False
    )

    use_llm_refiner = False
    if hasattr(args, "llm_refiner") and args.llm_refiner:
        use_llm_refiner = True

    # Build Pydantic Config Model
    config = DocvertConfig(
        language_hint=getattr(args, "language_hint", "auto"),
        ocr_languages=getattr(args, "ocr_languages", ["ko", "en"]),
        heading_mode=getattr(args, "heading_mode", "auto"),
        comment_mode=getattr(args, "comment_mode", "preserve"),
        footnote_mode=getattr(args, "footnote_mode", "preserve"),
        image_mode=getattr(args, "image_mode", "extract_link"),
        table_mode=getattr(args, "table_mode", "markdown_preferred"),
        pdf_reading_order_mode=getattr(args, "pdf_reading_order_mode", "auto"),
        include_headers_footers=getattr(args, "include_headers_footers", False),
        normalize_heading_levels=getattr(args, "normalize_heading_levels", True),
        preserve_numbering=getattr(args, "preserve_numbering", True),
        continue_on_error=continue_on_error,
        cache_by_hash=cache_by_hash,
        deterministic=getattr(args, "deterministic", True),
        aggressive_heading_inference=getattr(
            args, "aggressive_heading_inference", False
        ),
        use_llm_refiner=use_llm_refiner,
        llm_model=getattr(args, "llm_model", "gpt-4o-mini"),
    )

    # Process
    output_dir = getattr(args, "output_dir", Path("./out"))
    processor = BatchProcessor(config=config, output_dir=output_dir)
    processor.process(unique_target_files)


if __name__ == "__main__":
    main()
