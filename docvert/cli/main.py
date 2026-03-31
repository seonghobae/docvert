"""Command-line interface module for Docvert."""

import argparse
import sys
from pathlib import Path
from typing import List

from docvert.models.config import DocvertConfig

try:
    from docvert.core.batch import BatchProcessor
except ImportError:
    # Stub for BatchProcessor if it's not yet implemented
    class BatchProcessor:  # type: ignore
        """Stub for BatchProcessor."""
        def __init__(self, config: DocvertConfig):
            """Initialize stub."""
            self.config = config

        def process(self, files: List[Path]) -> None:
            """Process stub."""
            print(f"Stub: Processing {len(files)} files with config:")
            print(self.config.model_dump_json(indent=2))


def parse_args() -> argparse.Namespace:
    """Parses command line arguments for the Docvert CLI.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Docvert: Convert documents to Markdown."
    )

    # Input arguments
    parser.add_argument(
        "inputs", nargs="*", type=Path, help="Input files or directories to process."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        help="Input directory (alternative to positional arguments).",
    )

    # Config arguments
    parser.add_argument("--language-hint", choices=["ko", "en", "auto"], default="auto")
    parser.add_argument(
        "--ocr-languages",
        nargs="+",
        default=["ko", "en"],
        help="List of OCR languages (e.g., ko en)",
    )
    parser.add_argument(
        "--heading-mode", choices=["auto", "style_only", "heuristic"], default="auto"
    )
    parser.add_argument(
        "--comment-mode",
        choices=["preserve", "appendix", "inline", "drop"],
        default="preserve",
    )
    parser.add_argument(
        "--footnote-mode",
        choices=["preserve", "appendix", "inline"],
        default="preserve",
    )
    parser.add_argument(
        "--image-mode",
        choices=["extract_link", "embed", "extract_with_ocr", "skip"],
        default="extract_link",
    )
    parser.add_argument(
        "--table-mode",
        choices=["markdown_preferred", "html_for_complex"],
        default="markdown_preferred",
    )
    parser.add_argument(
        "--pdf-reading-order-mode",
        choices=["auto", "layout_strict", "ocr_fallback"],
        default="auto",
    )

    # Boolean flags
    parser.add_argument(
        "--include-headers-footers",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument(
        "--normalize-heading-levels",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--preserve-numbering", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument(
        "--continue-on-error", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument(
        "--cache-by-hash", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument(
        "--deterministic", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument(
        "--aggressive-heading-inference",
        action=argparse.BooleanOptionalAction,
        default=False,
    )

    parser.add_argument(
        "--use-llm-refiner",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Use LLM agent to refine the generated markdown output.",
    )
    parser.add_argument(
        "--llm-model",
        type=str,
        default="gpt-4o-mini",
        help="The LLM model to use for refinement (default: gpt-4o-mini).",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point for the Docvert command line interface.

    Parses arguments, gathers input files, dedupes them, builds the configuration,
    and runs the BatchProcessor to convert documents to Markdown.
    """
    args = parse_args()

    # Gather inputs
    target_files: List[Path] = []

    if args.inputs:
        for p in args.inputs:
            if p.is_file():
                target_files.append(p)
            elif p.is_dir():
                target_files.extend(f for f in p.rglob("*") if f.is_file())
            else:
                print(f"Warning: '{p}' does not exist.", file=sys.stderr)

    if args.input_dir:
        if not args.input_dir.is_dir():
            print(f"Error: '{args.input_dir}' is not a directory.", file=sys.stderr)
            sys.exit(1)
        target_files.extend(f for f in args.input_dir.rglob("*") if f.is_file())

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

    # Build Pydantic Config Model
    config = DocvertConfig(
        language_hint=args.language_hint,
        ocr_languages=args.ocr_languages,
        heading_mode=args.heading_mode,
        comment_mode=args.comment_mode,
        footnote_mode=args.footnote_mode,
        image_mode=args.image_mode,
        table_mode=args.table_mode,
        pdf_reading_order_mode=args.pdf_reading_order_mode,
        include_headers_footers=args.include_headers_footers,
        normalize_heading_levels=args.normalize_heading_levels,
        preserve_numbering=args.preserve_numbering,
        continue_on_error=args.continue_on_error,
        cache_by_hash=args.cache_by_hash,
        deterministic=args.deterministic,
        aggressive_heading_inference=args.aggressive_heading_inference,
        use_llm_refiner=args.use_llm_refiner,
        llm_model=args.llm_model,
    )

    # Process
    processor = BatchProcessor(config=config)
    processor.process(unique_target_files)


if __name__ == "__main__":
    main()
