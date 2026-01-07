"""Content chunking for handling large text files."""

from typing import List


def chunk_content(content: str, max_chunk_length: int = 10000) -> List[str]:
    """Split content into chunks for processing.
    
    When content is too large to process in a single LLM call, this function
    splits it into smaller chunks while trying to respect line boundaries.
    
    Args:
        content: Content to chunk.
        max_chunk_length: Maximum characters per chunk (default: 10000).
    
    Returns:
        List of content chunks.
    """
    if len(content) <= max_chunk_length:
        return [content]
    
    chunks = []
    lines = content.split("\n")
    current_chunk = []
    current_length = 0
    
    for line in lines:
        line_length = len(line)
        
        # If adding this line would exceed the limit and we have content
        if current_length + line_length > max_chunk_length and current_chunk:
            # Save current chunk and start new one
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_length = line_length
        else:
            # Add line to current chunk
            current_chunk.append(line)
            current_length += line_length + 1  # +1 for newline
    
    # Add any remaining content
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    
    return chunks

