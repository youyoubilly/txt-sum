"""Output formatting and file writing."""

from pathlib import Path


def write_markdown_summary(
    output_file: Path,
    source_file: Path,
    summary: str
) -> None:
    """Write summary to markdown file.
    
    Args:
        output_file: Path to output markdown file.
        source_file: Original source file path (for metadata).
        summary: Summary text content.
    """
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Format markdown content
    markdown_content = f"""# Summary: {source_file.name}

**Source File:** `{source_file.name}`

---

{summary}
"""
    
    # Write to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)


def format_markdown_summary(source_file: Path, summary: str) -> str:
    """Format summary as markdown (without writing to file).
    
    Args:
        source_file: Original source file path (for metadata).
        summary: Summary text content.
    
    Returns:
        Formatted markdown string.
    """
    return f"""# Summary: {source_file.name}

**Source File:** `{source_file.name}`

---

{summary}
"""

