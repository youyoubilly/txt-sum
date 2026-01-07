"""File operation utilities."""

from pathlib import Path
from typing import Optional, List
from charset_normalizer import detect


def detect_encoding(file_path: Path) -> str:
    """Detect file encoding.
    
    Args:
        file_path: Path to file.
    
    Returns:
        Detected encoding (defaults to 'utf-8').
    """
    with open(file_path, "rb") as f:
        raw_data = f.read()
        result = detect(raw_data)
        if result:
            encoding = result.get("encoding", "utf-8")
            # Handle common encoding issues
            if encoding.lower() in ["ascii", "windows-1252"]:
                encoding = "utf-8"
            return encoding
    return "utf-8"


def is_binary_file(file_path: Path, sample_size: int = 512) -> bool:
    """Check if a file is binary.
    
    Args:
        file_path: Path to file.
        sample_size: Number of bytes to sample (default: 512).
    
    Returns:
        True if file appears to be binary, False otherwise.
    """
    try:
        with open(file_path, "rb") as f:
            sample = f.read(sample_size)
        
        # Check for null bytes
        if b'\x00' in sample:
            return True
        
        # Use charset-normalizer to detect
        result = detect(sample)
        if result:
            encoding = result.get("encoding", "").lower()
            # If encoding detection fails or returns binary indicators
            if not encoding or encoding in ["binary", "unknown"]:
                return True
        
        # Check for high ratio of non-text characters
        text_chars = sum(1 for byte in sample if 32 <= byte < 127 or byte in [9, 10, 13])
        if len(sample) > 0 and text_chars / len(sample) < 0.7:
            return True
        
        return False
    except Exception:
        # If we can't read it, assume it might be binary
        return True


def is_text_file(file_path: Path) -> bool:
    """Check if a file is text-based.
    
    Args:
        file_path: Path to file.
    
    Returns:
        True if file appears to be text-based, False otherwise.
    """
    return not is_binary_file(file_path)


def get_output_path(input_file: Path, output_dir: Optional[Path] = None) -> Path:
    """Get expected output path for an input file.
    
    Args:
        input_file: Path to input file.
        output_dir: Optional output directory. If None, uses same directory as input.
    
    Returns:
        Expected output file path.
    """
    if output_dir:
        return output_dir / f"{input_file.stem}.md"
    else:
        return input_file.with_suffix(".md")


def discover_text_files(
    directory: Path,
    force_text: bool = False,
    supported_extensions: Optional[set] = None
) -> List[Path]:
    """Discover all text files in a directory (top-level only).
    
    Args:
        directory: Path to directory to scan.
        force_text: If True, attempt to process unknown file types.
        supported_extensions: Set of known subtitle extensions. If None, uses default.
    
    Returns:
        List of text file paths found in the directory.
    
    Raises:
        ValueError: If directory cannot be read.
    """
    if supported_extensions is None:
        supported_extensions = {".srt", ".txt", ".vtt", ".ass", ".ssa"}
    
    text_files = []
    
    try:
        for item in directory.iterdir():
            if not item.is_file():
                continue
            
            suffix = item.suffix.lower()
            
            # Known subtitle formats - always include
            if suffix in supported_extensions:
                text_files.append(item)
            # Unknown extensions - check if text-based
            elif force_text or is_text_file(item):
                text_files.append(item)
            # Skip binary files unless force_text is True
            elif force_text:
                text_files.append(item)
    
    except PermissionError:
        raise ValueError(f"Permission denied: Cannot read directory {directory}")
    except Exception as e:
        raise ValueError(f"Error scanning directory {directory}: {e}")
    
    return sorted(text_files)


def check_file_size(file_path: Path, warn_threshold_mb: float = 10.0) -> bool:
    """Check file size and warn if large.
    
    Args:
        file_path: Path to file.
        warn_threshold_mb: Size threshold in MB to warn about (default: 10.0).
    
    Returns:
        True if file is larger than threshold, False otherwise.
    """
    try:
        size_bytes = file_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        return size_mb > warn_threshold_mb
    except Exception:
        return False

