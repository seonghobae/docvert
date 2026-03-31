"""Document writer module for saving converted content and metadata."""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List

from docvert.models.document import Document


class Writer:
    """Handles writing document outputs, metadata, and assets to the filesystem.

    Args:
        output_dir (Path): The directory where all outputs will be written.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_markdown(self, document: Document, relative_stem: str) -> Path:
        """Writes a Document's markdown representation to a file.

        Args:
            document (Document): The parsed document to write.
            relative_stem (str): The filename stem (without extension).

        Returns:
            Path: Path to the written markdown file.
        """
        output_path = self.output_dir / f"{relative_stem}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(document.to_markdown())
        return output_path

    def write_markdown_string(self, markdown_content: str, relative_stem: str) -> Path:
        """Writes a Markdown string to a file.

        Args:
            markdown_content (str): The markdown string to write.
            relative_stem (str): The filename stem (without extension).

        Returns:
            Path: Path to the written markdown file.
        """
        output_path = self.output_dir / f"{relative_stem}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        return output_path

    def write_json_sidecar(self, metadata: Dict[str, Any], relative_stem: str) -> Path:
        """Writes a JSON sidecar file containing metadata.

        Args:
            metadata (Dict[str, Any]): Metadata dictionary to serialize.
            relative_stem (str): The filename stem (without extension).

        Returns:
            Path: Path to the written JSON file.
        """
        output_path = self.output_dir / f"{relative_stem}.conversion.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2, sort_keys=True)
        return output_path

    def create_assets_dir(self, relative_stem: str) -> Path:
        """Creates a directory for storing assets (e.g., images) related to a document.

        Args:
            relative_stem (str): The filename stem of the associated document.

        Returns:
            Path: Path to the created assets directory.
        """
        assets_dir = self.output_dir / f"{relative_stem}.assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        return assets_dir

    def write_batch_summary(self, summaries: List[Dict[str, Any]]) -> Path:
        """Writes a batch summary file in JSONL format.

        Args:
            summaries (List[Dict[str, Any]]): List of summary dictionaries for each processed file.

        Returns:
            Path: Path to the written batch summary file.
        """
        output_path = self.output_dir / "batch-summary.jsonl"
        with open(output_path, "w", encoding="utf-8") as f:
            for s in summaries:
                f.write(json.dumps(s, ensure_ascii=False, sort_keys=True) + "\n")
        return output_path

    def write_csv(
        self, filename: str, fieldnames: List[str], rows: List[Dict[str, Any]]
    ) -> Path:
        """Writes a list of dictionaries to a CSV file.

        Args:
            filename (str): Name of the CSV file.
            fieldnames (List[str]): List of column names for the CSV header.
            rows (List[Dict[str, Any]]): List of row dictionaries.

        Returns:
            Path: Path to the written CSV file.
        """
        output_path = self.output_dir / filename
        if not rows:
            return output_path

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return output_path
