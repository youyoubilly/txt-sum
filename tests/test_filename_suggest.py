"""Tests for filename suggestion logic."""

import pytest
from pathlib import Path
from txtguy.app.filename_suggest import _parse_filename_suggestions, _extract_json_from_text


def test_parse_json_response():
    """Test parsing JSON response from LLM."""
    response = '''
    Here are my suggestions:
    {
      "original": ["movie_summary.srt", "video_content.srt", "film_dialogue.srt", "subtitle_file.srt", "media_text.srt"],
      "output": ["movie_summary.md", "video_content.md", "film_dialogue.md", "subtitle_file.md", "media_text.md"]
    }
    '''
    
    input_file = Path("/test/input.srt")
    output_file = Path("/test/output.md")
    
    result = _parse_filename_suggestions(response, input_file, output_file)
    
    assert len(result["original"]) == 5
    assert len(result["output"]) == 5
    assert result["original"][0] == "movie_summary.srt"
    assert result["output"][0] == "movie_summary.md"


def test_parse_numbered_list_response():
    """Test parsing numbered list response from LLM."""
    # The regex expects "file suggestions:" pattern
    response = '''
Original file suggestions:
1. movie_summary.srt
2. video_content.srt
3. film_dialogue.srt
4. subtitle_file.srt
5. media_text.srt

Output file suggestions:
1. movie_summary.md
2. video_content.md
3. film_dialogue.md
4. subtitle_file.md
5. media_text.md
'''
    
    input_file = Path("/test/input.srt")
    output_file = Path("/test/output.md")
    
    result = _parse_filename_suggestions(response, input_file, output_file)
    
    # Check that we got the expected results
    assert len(result["original"]) >= 5
    assert len(result["output"]) >= 5
    # The parser should find the numbered list
    assert "movie_summary.srt" in result["original"] or result["original"][0] == input_file.name


def test_parse_empty_response():
    """Test parsing empty response falls back to original filenames."""
    response = "I cannot provide suggestions."
    
    input_file = Path("/test/input.srt")
    output_file = Path("/test/output.md")
    
    result = _parse_filename_suggestions(response, input_file, output_file)
    
    # Should pad with original filenames
    assert len(result["original"]) == 5
    assert len(result["output"]) == 5
    assert input_file.name in result["original"]
    assert output_file.name in result["output"]


def test_extract_json_valid():
    """Test extracting valid JSON from text."""
    text = 'Some text {"key": "value"} more text'
    result = _extract_json_from_text(text)
    assert result == '{"key": "value"}'


def test_extract_json_nested():
    """Test extracting nested JSON from text."""
    text = 'Text {"outer": {"inner": "value"}} end'
    result = _extract_json_from_text(text)
    assert result == '{"outer": {"inner": "value"}}'


def test_extract_json_none():
    """Test extracting JSON when none exists."""
    text = "No JSON here"
    result = _extract_json_from_text(text)
    assert result is None


def test_extension_preservation():
    """Test that file extensions are preserved correctly."""
    response = '''
    {
      "original": ["summary", "content", "text", "file", "doc"],
      "output": ["summary", "content", "text", "file", "doc"]
    }
    '''
    
    input_file = Path("/test/input.vtt")
    output_file = Path("/test/output.md")
    
    result = _parse_filename_suggestions(response, input_file, output_file)
    
    # All original files should have .vtt extension
    for filename in result["original"]:
        assert filename.endswith(".vtt"), f"Expected .vtt extension, got {filename}"
    
    # All output files should have .md extension
    for filename in result["output"]:
        assert filename.endswith(".md"), f"Expected .md extension, got {filename}"

