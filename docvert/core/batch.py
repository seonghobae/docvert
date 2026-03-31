import hashlib
import json
import logging
from pathlib import Path
from typing import List, Union, Optional, Dict, Any

from docvert.models.config import DocvertConfig
from docvert.core.writer import Writer
from docvert.parsers.docx_parser import DocxParser
from docvert.parsers.pdf_parser import PdfParser

logger = logging.getLogger(__name__)


def calculate_md5(file_path: Path) -> str:
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


class BatchProcessor:
    def __init__(
        self, config: DocvertConfig, output_dir: Optional[Union[str, Path]] = None
    ):
        self.config = config
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path.cwd()

        self.writer = Writer(self.output_dir)
        self.docx_parser = DocxParser(config=self.config)
        self.pdf_parser = PdfParser(config=self.config)

    def process(self, input_paths: List[Union[str, Path]]) -> None:
        summaries = []
        failures = []
        warnings = []

        for path in input_paths:
            path = Path(path)
            try:
                result = self.process_file(path)
                if result:
                    summaries.append(result)
                    if result.get("warnings"):
                        for w in result["warnings"]:
                            warnings.append(
                                {"source_file": str(path), "warning": str(w)}
                            )
            except Exception as e:
                if self.config.continue_on_error:
                    logger.error(f"Failed to process {path}: {e}")
                    failures.append({"source_file": str(path), "error": str(e)})
                else:
                    raise

        # Write summaries
        if summaries:
            self.writer.write_batch_summary(summaries)

        logger.info(
            f"Processed {len(summaries)} files. "
            f"Failures: {len(failures)}. Warnings: {len(warnings)}"
        )

        # Write CSVs
        if failures:
            self.writer.write_csv("failures.csv", ["source_file", "error"], failures)
        if warnings:
            self.writer.write_csv("warnings.csv", ["source_file", "warning"], warnings)

    def process_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        file_path = Path(file_path)
        stem = file_path.stem
        ext = file_path.suffix.lower()

        # Check cache
        file_hash = ""
        if self.config.cache_by_hash:
            file_hash = calculate_md5(file_path)
            json_path = self.output_dir / f"{stem}.conversion.json"
            if json_path.exists():
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        cached_meta = json.load(f)
                    if cached_meta.get("file_hash") == file_hash:
                        md_path = self.output_dir / f"{stem}.md"
                        if md_path.exists():
                            logger.info(f"Skipping {file_path} (cache hit)")
                            return cached_meta
                except Exception:
                    pass  # ignore error and proceed

        if ext == ".docx":
            parser = self.docx_parser
        elif ext == ".pdf":
            parser = self.pdf_parser
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        parser_path_used = parser.__class__.__name__

        doc = parser.parse(file_path)

        # Extract metadata
        output_md_path = self.writer.write_markdown(doc, stem)
        self.writer.create_assets_dir(stem)

        metadata = {
            "source_file": str(file_path),
            "input_format": ext,
            "output_file": str(output_md_path),
            "parser_path_used": parser_path_used,
            "file_hash": file_hash or calculate_md5(file_path),
            "warnings": doc.metadata.get("warnings", []),
            "confidence": doc.metadata.get("confidence", 1.0),
        }

        self.writer.write_json_sidecar(metadata, stem)

        return metadata
