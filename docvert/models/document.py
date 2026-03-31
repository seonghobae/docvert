from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Block:
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Paragraph(Block):
    pass


@dataclass
class Heading(Block):
    level: int = 1
    score: int = 100


@dataclass
class Table(Block):
    rows: List[List[str]] = field(default_factory=list)


@dataclass
class Document:
    blocks: List[Block] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
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
        return "\n".join(lines)
