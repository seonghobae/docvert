import json
import csv
from pathlib import Path
from typing import Dict, Any, List

from docvert.models.document import Document


class Writer:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_markdown(self, document: Document, relative_stem: str) -> Path:
        output_path = self.output_dir / f"{relative_stem}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(document.to_markdown())
        return output_path

    def write_json_sidecar(self, metadata: Dict[str, Any], relative_stem: str) -> Path:
        output_path = self.output_dir / f"{relative_stem}.conversion.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2, sort_keys=True)
        return output_path

    def create_assets_dir(self, relative_stem: str) -> Path:
        assets_dir = self.output_dir / f"{relative_stem}.assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        return assets_dir

    def write_batch_summary(self, summaries: List[Dict[str, Any]]) -> Path:
        output_path = self.output_dir / "batch-summary.jsonl"
        with open(output_path, "w", encoding="utf-8") as f:
            for s in summaries:
                f.write(json.dumps(s, ensure_ascii=False, sort_keys=True) + "\n")
        return output_path

    def write_csv(
        self, filename: str, fieldnames: List[str], rows: List[Dict[str, Any]]
    ) -> Path:
        output_path = self.output_dir / filename
        if not rows:
            return output_path

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return output_path
