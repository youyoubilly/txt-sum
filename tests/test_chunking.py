"""Tests for chunking logic."""

import pytest
from txt_sum.app.chunking import chunk_content


def test_chunk_content_small():
    """Test that small content is not chunked."""
    content = "This is a small piece of content."
    chunks = chunk_content(content, max_chunk_length=100)
    assert len(chunks) == 1
    assert chunks[0] == content


def test_chunk_content_large():
    """Test that large content is properly chunked."""
    # Create content with multiple lines
    lines = ["Line " + str(i) for i in range(100)]
    content = "\n".join(lines)
    
    chunks = chunk_content(content, max_chunk_length=50)
    
    # Should have multiple chunks
    assert len(chunks) > 1
    
    # All chunks should respect line boundaries
    for chunk in chunks:
        assert not chunk.startswith("\n")
        assert chunk.strip()  # No empty chunks


def test_chunk_content_exact_boundary():
    """Test chunking at exact boundary."""
    content = "A" * 100
    chunks = chunk_content(content, max_chunk_length=100)
    assert len(chunks) == 1


def test_chunk_content_empty():
    """Test empty content."""
    content = ""
    chunks = chunk_content(content, max_chunk_length=100)
    assert len(chunks) == 1
    assert chunks[0] == ""


def test_chunk_content_preserves_lines():
    """Test that chunking preserves line boundaries."""
    lines = ["First line", "Second line", "Third line", "Fourth line"]
    content = "\n".join(lines)
    
    chunks = chunk_content(content, max_chunk_length=20)
    
    # Reconstruct and verify no data loss
    reconstructed = "\n".join(chunks)
    # Note: chunking may add extra newlines between chunks
    assert all(line in reconstructed for line in lines)

