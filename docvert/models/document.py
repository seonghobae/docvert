"""Document structure models for representing parsed content."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Block:
    """Base class representing a logical block of content in a document.

    Attributes:
        content (str): The text content of the block.
        metadata (Dict[str, Any]): Additional metadata associated with the block.
    """

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Paragraph(Block):
    """Class representing a paragraph block in a document."""

    pass


@dataclass
class Heading(Block):
    """Class representing a heading block in a document.

    Attributes:
        level (int): The heading level (e.g., 1 for H1, 2 for H2).
        score (int): A confidence score representing the certainty that this block is a heading.
    """

    level: int = 1
    score: int = 100


@dataclass
class Table(Block):
    """Class representing a table block in a document.

    Attributes:
        rows (List[List[str]]): The rows of the table, where each row is a list of cell strings.
    """

    rows: List[List[str]] = field(default_factory=list)


@dataclass
class Image(Block):
    """Class representing an image block in a document.

    Attributes:
        alt_text (str): Alternative text for the image.
        extension (Optional[str]): Image file extension (e.g., '.png').
        image_bytes (Optional[bytes]): Raw image data bytes.
        filepath (Optional[str]): Relative path where the image is saved.
    """

    alt_text: str = ""
    extension: Optional[str] = None
    image_bytes: Optional[bytes] = None
    filepath: Optional[str] = None


@dataclass
class Document:
    """Class representing a structured document composed of blocks.

    Attributes:
        blocks (List[Block]): The sequential list of blocks forming the document.
        metadata (Dict[str, Any]): Document-level metadata.
    """

    blocks: List[Block] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Converts the document's blocks into a Markdown string representation.

        Returns:
            str: The Markdown formatted string of the document content.
        """
        lines = []
        for block in self.blocks:
            if isinstance(block, Heading):
                lines.append(f"{'#' * block.level} {block.content}\n")
            elif isinstance(block, Paragraph):
                lines.append(f"{block.content}\n")
            elif isinstance(block, Table):
                for row in block.rows:
                    lines.append("| " + " | ".join(row) + " |")
                lines.append("\n")
            elif isinstance(block, Image):
                path = block.filepath or ""
                lines.append(f"![{block.alt_text}]({path})\n")
        return "\n".join(lines)
