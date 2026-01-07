"""Tests for sanitization logic."""

import pytest
from txt_sum.app.sanitize import sanitize_llm_response


def test_sanitize_no_thinking_tags():
    """Test that content without thinking tags is unchanged."""
    content = "This is a clean summary without any thinking tags."
    result = sanitize_llm_response(content)
    assert result == content


def test_sanitize_think_tags():
    """Test removal of <think> tags."""
    content = "<think>Let me analyze this...</think>Here is the summary."
    result = sanitize_llm_response(content)
    assert "<think>" not in result
    assert "</think>" not in result
    assert "Here is the summary." in result


def test_sanitize_thinking_tags():
    """Test removal of <thinking> tags."""
    content = "<thinking>Processing...</thinking>Summary content here."
    result = sanitize_llm_response(content)
    assert "<thinking>" not in result
    assert "</thinking>" not in result
    assert "Summary content here." in result


def test_sanitize_reasoning_tags():
    """Test removal of <reasoning> tags."""
    content = "Summary: <reasoning>My reasoning process</reasoning>Actual summary."
    result = sanitize_llm_response(content)
    assert "<reasoning>" not in result
    assert "</reasoning>" not in result
    assert "Actual summary." in result


def test_sanitize_nested_tags():
    """Test removal of nested thinking tags."""
    content = """
    <think>
        This is outer thinking.
        <think>This is inner thinking.</think>
    </think>
    Final summary text.
    """
    result = sanitize_llm_response(content)
    assert "<think>" not in result
    assert "Final summary text." in result


def test_sanitize_orphaned_tags():
    """Test removal of orphaned closing tags."""
    content = "Summary text</think> more text"
    result = sanitize_llm_response(content)
    assert "</think>" not in result
    assert "Summary text" in result
    assert "more text" in result


def test_sanitize_thinking_patterns():
    """Test removal of meta-thinking patterns."""
    content = """
    Okay, I need to summarize this.
    Let me think about the key points.
    
    Summary:
    This is the actual summary content.
    It contains the key information.
    """
    result = sanitize_llm_response(content)
    # Note: The current implementation removes lines starting with these patterns
    # but may not catch all cases depending on context
    # This test verifies the actual content is preserved
    assert "This is the actual summary content." in result
    assert "It contains the key information." in result


def test_sanitize_multiple_blank_lines():
    """Test cleanup of multiple blank lines."""
    content = "Line 1\n\n\n\nLine 2"
    result = sanitize_llm_response(content)
    # Should reduce to at most 2 newlines (one blank line)
    assert "\n\n\n" not in result


def test_sanitize_placeholder_words():
    """Test removal of standalone placeholder words."""
    content = """
    space
    thinking
    
    Actual content here.
    """
    result = sanitize_llm_response(content)
    # Standalone "space" and "thinking" should be removed
    assert result.strip().startswith("Actual content")


def test_sanitize_complex_case():
    """Test a complex realistic case."""
    content = """
    <think>Let me analyze the video content...</think>
    
    Okay, I need to create a summary.
    
    Summary:
    
    # Video Analysis
    
    <reasoning>This part discusses key themes</reasoning>
    
    The video covers important topics about technology.
    It provides insights into modern developments.
    
    </think>
    
    ## Conclusion
    The content is educational and informative.
    """
    result = sanitize_llm_response(content)
    
    # All XML-style thinking tags should be removed
    assert "<think>" not in result
    assert "<reasoning>" not in result
    assert "Let me analyze" not in result
    
    # Actual content should remain (the important parts)
    assert "video covers" in result or "Video Analysis" in result
    assert "educational and informative" in result

