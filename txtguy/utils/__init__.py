"""Utility modules for text file processing."""

from txtguy.utils.file_utils import (
    detect_encoding,
    is_binary_file,
    is_text_file,
    get_output_path,
    discover_text_files,
    check_file_size,
)
from txtguy.utils.text_utils import (
    sanitize_filename,
    extract_summary_from_markdown,
    clean_formatting,
)
from txtguy.utils.cli_utils import (
    read_context,
    interactive_filename_selection,
    rename_files,
)

__all__ = [
    "detect_encoding",
    "is_binary_file",
    "is_text_file",
    "get_output_path",
    "discover_text_files",
    "check_file_size",
    "sanitize_filename",
    "extract_summary_from_markdown",
    "clean_formatting",
    "read_context",
    "interactive_filename_selection",
    "rename_files",
]

