"""DOCX document parser module."""

import logging
from pathlib import Path
from typing import Optional, Any
import docx
import mammoth
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

from docvert.models.document import (
    Document,
    Block,
    Heading,
    Paragraph as DocvertParagraph,
    Table as DocvertTable,
)

logger = logging.getLogger(__name__)


class DocvertConfig:
    """A stub for the config class in case it doesn't exist yet."""

    pass


class DocxParser:
    """Parser for Microsoft Word (.docx) files.

    Extracts paragraphs, headings, and tables using python-docx with a fallback to mammoth.

    Args:
        config (Optional[Any]): Configuration object. Defaults to an empty DocvertConfig.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config or DocvertConfig()

    def parse(self, file_path: str | Path) -> Document:
        """Parses a DOCX file into a Document object.

        Attempts to use python-docx first. If it fails, falls back to mammoth.

        Args:
            file_path (str | Path): Path to the DOCX file.

        Returns:
            Document: The parsed document structure.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            return self._parse_with_python_docx(file_path)
        except Exception as e:
            logger.warning(f"python-docx failed: {e}. Falling back to mammoth.")
            return self._parse_with_mammoth(file_path)

    def _parse_with_python_docx(self, file_path: Path) -> Document:
        """Parses a DOCX file using python-docx.

        Args:
            file_path (Path): Path to the DOCX file.

        Returns:
            Document: The parsed document.
        """
        doc: _Document = docx.Document(file_path)
        docvert_doc = Document()

        for element in doc.element.body:
            if isinstance(element, CT_P):
                p = Paragraph(element, doc)
                if not p.text.strip():
                    continue
                block = self._process_paragraph(p)
                docvert_doc.blocks.append(block)
            elif element.tag.endswith("tbl"):
                # Very basic table handling
                for table in doc.tables:
                    if table._element == element:
                        docvert_doc.blocks.append(self._process_table(table))
                        break

        return docvert_doc

    def _process_paragraph(self, p: Paragraph) -> Block:
        """Processes a python-docx Paragraph into a Docvert Block.

        Determines if the paragraph is a heading or normal text based on styling and heuristics.

        Args:
            p (Paragraph): The python-docx paragraph element.

        Returns:
            Block: The corresponding Docvert block (Heading or Paragraph).
        """
        score, level = self._calculate_heading_score(p)
        text = p.text.strip()

        metadata = {"style": p.style.name if p.style else None, "score": score}

        if score >= 85:
            return Heading(content=text, level=level, score=score, metadata=metadata)
        elif score >= 70:
            logger.warning(f"Borderline heading (score {score}): {text[:30]}...")
            # We treat it as a heading or paragraph depending on config. We'll default to paragraph here with a warning.
            return DocvertParagraph(content=text, metadata=metadata)
        else:
            return DocvertParagraph(content=text, metadata=metadata)

    def _calculate_heading_score(self, p: Paragraph) -> tuple[int, int]:
        """Heuristics to determine if a paragraph is a heading.

        Args:
            p (Paragraph): The python-docx paragraph element.

        Returns:
            tuple[int, int]: A tuple containing the confidence score (0-100) and candidate heading level.
                score >= 85 -> heading
                score 70-84 -> warning, maybe heading
                score < 70 -> regular paragraph
        """
        score = 0
        level = 1

        style_name = p.style.name.lower() if p.style else ""

        # 1. Built-in styles
        if "heading" in style_name:
            score += 90
            try:
                # 'Heading 1' -> level 1
                level = int(style_name.split()[-1])
            except ValueError:
                level = 1

        # 2. Outline level (often 0 for body text, 1-9 for headings in word)
        # Using a simplified check, if outline_level is 0, it's body text (or top level depending on Word version)
        if p.style and hasattr(p.style, "paragraph_format"):
            outline_level = p.style.paragraph_format.outline_level
            # In docx, NO_OUTLINE_LEVEL is usually 9 (for some versions) or None. Let's do a basic check
            if outline_level is not None and outline_level < 9:
                score += 50
                level = outline_level + 1

        # 3. Formatting heuristics
        runs = p.runs
        if runs:
            # Check if majority of text is bold
            bold_chars = sum(len(r.text) for r in runs if r.bold)
            total_chars = sum(len(r.text) for r in runs)
            if total_chars > 0 and (bold_chars / total_chars) > 0.8:
                score += 30

            # Check font size
            sizes = [r.font.size.pt for r in runs if r.font and r.font.size]
            if sizes:
                avg_size = sum(sizes) / len(sizes)
                if avg_size >= 14:
                    score += 40
                elif avg_size >= 12:
                    score += 20

        # Max score is capped
        score = min(score, 100)

        return score, level

    def _process_table(self, table: Table) -> DocvertTable:
        """Processes a python-docx Table into a Docvert Table block.

        Args:
            table (Table): The python-docx table element.

        Returns:
            DocvertTable: The parsed table block.
        """
        rows_data = []
        for row in table.rows:
            row_data = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            rows_data.append(row_data)
        return DocvertTable(content="", rows=rows_data)

    def _parse_with_mammoth(self, file_path: Path) -> Document:
        """Fallback method using mammoth to parse DOCX to Markdown, then to a Document.

        Args:
            file_path (Path): Path to the DOCX file.

        Returns:
            Document: The parsed document structure.
        """
        with open(file_path, "rb") as docx_file:
            result = mammoth.convert_to_markdown(docx_file)
            md_text = result.value

            # Simple conversion from markdown to Docvert Document
            docvert_doc = Document()
            for line in md_text.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    level = len(line.split(" ")[0])
                    content = line[level:].strip()
                    docvert_doc.blocks.append(
                        Heading(content=content, level=level, score=100)
                    )
                else:
                    docvert_doc.blocks.append(DocvertParagraph(content=line))

            return docvert_doc
