from typing import Any
from pathlib import Path
from docvert.models.document import Document, Image
from docvert.models.config import DocvertConfig
from docvert.core.batch import BatchProcessor

class MockParser:
    def parse(self, *args: Any, **kwargs: Any) -> Any:
        return Document(blocks=[Image(content="", alt_text="mock", image_bytes=b"mockbytes", extension=".png")])

def test_batch_processor_saves_images(tmp_path: Path, monkeypatch: Any)   -> None:
    config = DocvertConfig()
    processor = BatchProcessor(config=config, output_dir=tmp_path)
    
    # Mock docx_parser
    processor.docx_parser = MockParser()  # type: ignore[assignment]
    
    file_path = tmp_path / "test.docx"
    file_path.touch()
    
    # Process
    processor.process_file(file_path)
    
    # Check if assets dir is created
    assets_dir = tmp_path / "test.assets"
    assert assets_dir.exists()
    
    # Check if image file is created
    img_path = assets_dir / "image_0.png"
    assert img_path.exists()
    assert img_path.read_bytes() == b"mockbytes"
    
    # Check if markdown contains the correct path
    md_path = tmp_path / "test.md"
    assert "![mock](test.assets/image_0.png)" in md_path.read_text()
