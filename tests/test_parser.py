"""Tests for parser logic."""

import pytest
from pathlib import Path
import tempfile
from txtguy.parser import SubtitleParser, SubtitleEntry


def test_parse_txt_file():
    """Test parsing a simple text file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Line 1\nLine 2\nLine 3")
        temp_path = Path(f.name)
    
    try:
        entries = SubtitleParser.parse(temp_path)
        assert len(entries) == 3
        assert entries[0].text == "Line 1"
        assert entries[1].text == "Line 2"
        assert entries[2].text == "Line 3"
    finally:
        temp_path.unlink()


def test_extract_text_txt_file():
    """Test extracting text from a text file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Line 1\nLine 2\nLine 3")
        temp_path = Path(f.name)
    
    try:
        text = SubtitleParser.extract_text(temp_path)
        assert text == "Line 1\nLine 2\nLine 3"
    finally:
        temp_path.unlink()


def test_parse_empty_file():
    """Test parsing an empty file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("")
        temp_path = Path(f.name)
    
    try:
        entries = SubtitleParser.parse(temp_path)
        assert len(entries) == 0
    finally:
        temp_path.unlink()


def test_parse_paragraphs():
    """Test parsing text file with paragraphs."""
    content = "Paragraph 1\nContinued.\n\nParagraph 2\nAlso continued."
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)
    
    try:
        entries = SubtitleParser.parse(temp_path)
        # Should split by paragraphs
        assert len(entries) == 2
        assert "Paragraph 1" in entries[0].text
        assert "Paragraph 2" in entries[1].text
    finally:
        temp_path.unlink()


def test_subtitle_entry():
    """Test SubtitleEntry class."""
    entry = SubtitleEntry(
        text="Test subtitle",
        start_time="00:00:01,000",
        end_time="00:00:03,000",
        speaker="Speaker"
    )
    
    assert entry.text == "Test subtitle"
    assert entry.start_time == "00:00:01,000"
    assert entry.end_time == "00:00:03,000"
    assert entry.speaker == "Speaker"
    assert str(entry) == "Test subtitle"


def test_force_text_binary():
    """Test force_text flag on binary-looking files."""
    # Create a file with actual binary content (null bytes)
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.dat', delete=False) as f:
        # Write binary content with null bytes to trigger binary detection
        f.write(b'Binary\x00content\x00here\n')
        temp_path = Path(f.name)
    
    try:
        # Without force_text, should raise ValueError for binary files
        with pytest.raises(ValueError, match="binary"):
            SubtitleParser.parse(temp_path, force_text=False)
        
        # With force_text, should work (though may not parse well)
        entries = SubtitleParser.parse(temp_path, force_text=True)
        # Just verify it doesn't crash
        assert isinstance(entries, list)
    finally:
        temp_path.unlink()

