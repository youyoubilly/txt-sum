"""Domain types for txt-sum."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ParsedContent:
    """Parsed text content from a file."""
    text: str
    file_path: Path
    length: int
    
    def __post_init__(self):
        if self.length is None:
            self.length = len(self.text)


@dataclass
class SummaryRequest:
    """Request to summarize content."""
    content: str
    prompt_template: Optional[str] = None
    language: str = "en"
    extra_context: Optional[str] = None


@dataclass
class Summary:
    """Generated summary result."""
    text: str
    source_file: Path
    request: SummaryRequest

