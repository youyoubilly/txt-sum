"""Text file parsers for various formats."""

import re
from pathlib import Path
from typing import List, Tuple, Optional
import pysrt
import webvtt
from txt_sum.utils.file_utils import detect_encoding, is_binary_file, is_text_file


class SubtitleEntry:
    """Represents a single subtitle entry."""
    
    def __init__(self, text: str, start_time: Optional[str] = None, 
                 end_time: Optional[str] = None, speaker: Optional[str] = None):
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.speaker = speaker
    
    def __str__(self) -> str:
        return self.text


class SubtitleParser:
    """Base class for text file parsers."""
    
    @classmethod
    def parse(cls, file_path: Path, force_text: bool = False) -> List[SubtitleEntry]:
        """Parse text file.
        
        Args:
            file_path: Path to text file.
            force_text: If True, attempt to process unknown file types.
        
        Returns:
            List of subtitle entries.
        
        Raises:
            ValueError: If file format is not supported or file is binary.
        """
        # Check if file is binary
        if is_binary_file(file_path) and not force_text:
            raise ValueError(f"File appears to be binary: {file_path}")
        
        suffix = file_path.suffix.lower()
        
        # Known subtitle formats - use specialized parsers
        if suffix == ".srt":
            return SRTParser.parse(file_path)
        elif suffix == ".txt":
            return TXTParser.parse(file_path)
        elif suffix == ".vtt":
            return VTTParser.parse(file_path)
        elif suffix in [".ass", ".ssa"]:
            return ASSParser.parse(file_path)
        else:
            # Unknown extension - try generic text parser
            if is_text_file(file_path) or force_text:
                return GenericTextParser.parse(file_path)
            else:
                raise ValueError(f"Unsupported file format: {suffix}. Use --force-text to process anyway.")
    
    @classmethod
    def extract_text(cls, file_path: Path, full_context: bool = False, force_text: bool = False) -> str:
        """Extract plain text from file.
        
        Args:
            file_path: Path to file.
            full_context: If True, preserve timestamps and formatting.
            force_text: If True, attempt to process unknown file types.
        
        Returns:
            Plain text content.
        """
        entries = cls.parse(file_path, force_text=force_text)
        
        if full_context:
            # Include timestamps and formatting
            texts = []
            for entry in entries:
                parts = []
                if entry.start_time and entry.end_time:
                    parts.append(f"[{entry.start_time} --> {entry.end_time}]")
                if entry.speaker:
                    parts.append(f"{entry.speaker}:")
                parts.append(entry.text)
                texts.append(" ".join(parts))
            return "\n".join(texts)
        else:
            # Extract only text content (timestamps excluded)
            texts = [entry.text for entry in entries if entry.text.strip()]
            return "\n".join(texts)


class GenericTextParser(SubtitleParser):
    """Parser for generic text files."""
    
    @classmethod
    def parse(cls, file_path: Path) -> List[SubtitleEntry]:
        """Parse generic text file.
        
        Args:
            file_path: Path to text file.
        
        Returns:
            List of subtitle entries (one per line or paragraph).
        """
        encoding = detect_encoding(file_path)
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()
        
        entries = []
        # Try paragraph mode first (double newline)
        if "\n\n" in content:
            paragraphs = content.split("\n\n")
            for para in paragraphs:
                text = para.strip().replace("\n", " ")
                if text:
                    entries.append(SubtitleEntry(text=text))
        else:
            # Line mode
            for line in content.split("\n"):
                text = line.strip()
                if text:
                    entries.append(SubtitleEntry(text=text))
        
        return entries


class SRTParser(SubtitleParser):
    """Parser for SRT (SubRip) format."""
    
    @classmethod
    def parse(cls, file_path: Path) -> List[SubtitleEntry]:
        """Parse SRT file.
        
        Args:
            file_path: Path to SRT file.
        
        Returns:
            List of subtitle entries.
        """
        encoding = detect_encoding(file_path)
        try:
            subs = pysrt.open(str(file_path), encoding=encoding)
            entries = []
            for sub in subs:
                entries.append(SubtitleEntry(
                    text=sub.text.replace("\n", " ").strip(),
                    start_time=str(sub.start),
                    end_time=str(sub.end)
                ))
            return entries
        except Exception as e:
            # Fallback to manual parsing if pysrt fails
            return cls._parse_manual(file_path, encoding)
    
    @classmethod
    def _parse_manual(cls, file_path: Path, encoding: str) -> List[SubtitleEntry]:
        """Manual SRT parsing fallback."""
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()
        
        entries = []
        # SRT format: number, timestamp, text, blank line
        pattern = r"(\d+)\s*\n(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*\n(.*?)(?=\n\d+\s*\n|\n*$)"
        
        for match in re.finditer(pattern, content, re.DOTALL):
            text = match.group(4).strip().replace("\n", " ")
            if text:
                entries.append(SubtitleEntry(
                    text=text,
                    start_time=match.group(2),
                    end_time=match.group(3)
                ))
        
        return entries


class TXTParser(SubtitleParser):
    """Parser for plain text files."""
    
    @classmethod
    def parse(cls, file_path: Path) -> List[SubtitleEntry]:
        """Parse TXT file.
        
        Args:
            file_path: Path to TXT file.
        
        Returns:
            List of subtitle entries (one per line or paragraph).
        """
        encoding = detect_encoding(file_path)
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()
        
        entries = []
        # Try paragraph mode first (double newline)
        if "\n\n" in content:
            paragraphs = content.split("\n\n")
            for para in paragraphs:
                text = para.strip().replace("\n", " ")
                if text:
                    entries.append(SubtitleEntry(text=text))
        else:
            # Line mode
            for line in content.split("\n"):
                text = line.strip()
                if text:
                    entries.append(SubtitleEntry(text=text))
        
        return entries


class VTTParser(SubtitleParser):
    """Parser for VTT (WebVTT) format."""
    
    @classmethod
    def parse(cls, file_path: Path) -> List[SubtitleEntry]:
        """Parse VTT file.
        
        Args:
            file_path: Path to VTT file.
        
        Returns:
            List of subtitle entries.
        """
        encoding = detect_encoding(file_path)
        try:
            vtt = webvtt.read(str(file_path), encoding=encoding)
            entries = []
            for caption in vtt:
                text = caption.text.replace("\n", " ").strip()
                if text:
                    entries.append(SubtitleEntry(
                        text=text,
                        start_time=str(caption.start),
                        end_time=str(caption.end)
                    ))
            return entries
        except Exception as e:
            # Fallback to manual parsing
            return cls._parse_manual(file_path, encoding)
    
    @classmethod
    def _parse_manual(cls, file_path: Path, encoding: str) -> List[SubtitleEntry]:
        """Manual VTT parsing fallback."""
        with open(file_path, "r", encoding=encoding) as f:
            lines = f.readlines()
        
        entries = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Skip WEBVTT header and metadata
            if line.startswith("WEBVTT") or line.startswith("NOTE") or not line:
                i += 1
                continue
            
            # Check if this is a timestamp line
            if " --> " in line:
                times = line.split(" --> ")
                if len(times) == 2:
                    start_time = times[0].strip()
                    end_time = times[1].strip()
                    # Collect text until next timestamp or blank line
                    i += 1
                    text_lines = []
                    while i < len(lines) and lines[i].strip() and " --> " not in lines[i]:
                        text_lines.append(lines[i].strip())
                        i += 1
                    text = " ".join(text_lines)
                    if text:
                        entries.append(SubtitleEntry(
                            text=text,
                            start_time=start_time,
                            end_time=end_time
                        ))
                    continue
            i += 1
        
        return entries


class ASSParser(SubtitleParser):
    """Parser for ASS/SSA (Advanced SubStation Alpha) format."""
    
    @classmethod
    def parse(cls, file_path: Path) -> List[SubtitleEntry]:
        """Parse ASS/SSA file.
        
        Args:
            file_path: Path to ASS/SSA file.
        
        Returns:
            List of subtitle entries.
        """
        encoding = detect_encoding(file_path)
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()
        
        entries = []
        in_events = False
        
        for line in content.split("\n"):
            line = line.strip()
            
            # Find [Events] section
            if line == "[Events]":
                in_events = True
                continue
            
            # Stop at next section
            if in_events and line.startswith("["):
                break
            
            if in_events and line.startswith("Dialogue:"):
                # ASS format: Dialogue: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
                parts = line.split(",", 9)
                if len(parts) >= 10:
                    speaker = parts[4].strip() if len(parts) > 4 else None
                    text = parts[9].strip()
                    # Remove ASS formatting tags
                    text = cls._remove_ass_tags(text)
                    if text:
                        entries.append(SubtitleEntry(
                            text=text,
                            start_time=parts[1].strip() if len(parts) > 1 else None,
                            end_time=parts[2].strip() if len(parts) > 2 else None,
                            speaker=speaker
                        ))
        
        return entries
    
    @staticmethod
    def _remove_ass_tags(text: str) -> str:
        """Remove ASS/SSA formatting tags from text.
        
        Args:
            text: Text with ASS tags.
        
        Returns:
            Cleaned text.
        """
        # Remove all formatting tags: {\...} (font size, color, animation, etc.)
        text = re.sub(r"\{[^}]*\}", "", text)  # Remove {tags}
        # Remove control codes: \N (newline), \n, etc.
        text = text.replace("\\N", " ").replace("\\n", " ")
        # Remove \tag commands
        text = re.sub(r"\\[a-z]+", "", text, flags=re.IGNORECASE)
        # Remove style information and other control sequences
        text = re.sub(r"\\[0-9]+", "", text)  # Remove numeric codes
        return text.strip()

