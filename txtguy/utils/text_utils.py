"""Text processing utilities."""

import re
from pathlib import Path


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters.
    
    Args:
        filename: Filename to sanitize.
    
    Returns:
        Sanitized filename.
    """
    # Remove invalid characters: / \ : * ? " < > |
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Limit length (keep extension)
    if '.' in sanitized:
        name, ext = sanitized.rsplit('.', 1)
        if len(name) > 200:
            name = name[:200]
        sanitized = name + '.' + ext
    else:
        if len(sanitized) > 200:
            sanitized = sanitized[:200]
    
    return sanitized if sanitized else "unnamed"


def extract_summary_from_markdown(markdown_file: Path) -> str:
    """Extract summary text from markdown file.
    
    Args:
        markdown_file: Path to markdown file.
    
    Returns:
        Summary text content (without markdown header).
    """
    try:
        with open(markdown_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remove markdown header (everything before the first ---)
        if "---" in content:
            parts = content.split("---", 1)
            if len(parts) > 1:
                return parts[1].strip()
        
        # Fallback: return everything after first line
        lines = content.split("\n")
        if len(lines) > 1:
            return "\n".join(lines[1:]).strip()
        
        return content.strip()
    except Exception:
        return ""


def clean_formatting(text: str) -> str:
    """Clean formatting from text.
    
    Args:
        text: Text to clean.
    
    Returns:
        Cleaned text.
    """
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    # Remove multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

