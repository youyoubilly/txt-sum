"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a sample text file for testing."""
    file_path = temp_dir / "sample.txt"
    file_path.write_text("Line 1\nLine 2\nLine 3\n")
    return file_path


@pytest.fixture
def sample_srt_content():
    """Provide sample SRT content."""
    return """1
00:00:01,000 --> 00:00:03,000
First subtitle line

2
00:00:04,000 --> 00:00:06,000
Second subtitle line

3
00:00:07,000 --> 00:00:09,000
Third subtitle line
"""

