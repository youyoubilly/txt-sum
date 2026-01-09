"""Filename suggestion using LLM."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from txtguy.llm.providers.base import BaseLLMProvider
from txtguy.utils.text_utils import sanitize_filename


def suggest_filenames(
    input_file: Path,
    output_file: Path,
    summary: str,
    provider: BaseLLMProvider
) -> Dict[str, List[str]]:
    """Suggest better filenames using LLM based on summary content.
    
    Args:
        input_file: Original input file path.
        output_file: Output summary file path.
        summary: Summary text content.
        provider: LLM provider instance.
    
    Returns:
        Dictionary with keys "original" and "output", each containing a list of 5 filename suggestions.
        Returns empty lists if LLM call fails.
    """
    # Get brief excerpt from summary (first 800 chars)
    summary_excerpt = summary[:800] + ("..." if len(summary) > 800 else "")
    
    # Create prompt for filename suggestions
    prompt = f"""Based on the following information, suggest 5 better filenames for both the original file and its summary file.

Original filename: {input_file.name}
Output filename: {output_file.name}
Summary excerpt:
{summary_excerpt}

Please provide 5 filename suggestions for each file. The filenames should:
- Be descriptive and reflect the content
- Be valid filenames (no invalid characters like /, \\, :, *, ?, ", <, >, |)
- Be concise but meaningful
- Preserve the original file extension for the original file
- Use .md extension for the output file

Format your response as JSON:
{{
  "original": ["filename1{input_file.suffix}", "filename2{input_file.suffix}", "filename3{input_file.suffix}", "filename4{input_file.suffix}", "filename5{input_file.suffix}"],
  "output": ["filename1.md", "filename2.md", "filename3.md", "filename4.md", "filename5.md"]
}}

If you cannot format as JSON, provide a numbered list:
Original file suggestions:
1. filename1{input_file.suffix}
2. filename2{input_file.suffix}
3. filename3{input_file.suffix}
4. filename4{input_file.suffix}
5. filename5{input_file.suffix}

Output file suggestions:
1. filename1.md
2. filename2.md
3. filename3.md
4. filename4.md
5. filename5.md
"""
    
    try:
        response = provider.generate(prompt, "", max_tokens=500, temperature=0.7)
        return _parse_filename_suggestions(response, input_file, output_file)
    except Exception:
        return {"original": [], "output": []}


def suggest_filenames_from_content(
    input_file: Path,
    content_excerpt: str,
    provider: BaseLLMProvider
) -> Dict[str, List[str]]:
    """Suggest better filenames using LLM based on input file content.
    
    Args:
        input_file: Original input file path.
        content_excerpt: Excerpt of file content (first 1000-2000 chars).
        provider: LLM provider instance.
    
    Returns:
        Dictionary with keys "original" and "output", each containing a list of 5 filename suggestions.
        Returns empty lists if LLM call fails.
    """
    # Create output filename suggestion (use .md extension)
    output_base = input_file.stem + ".md"
    
    # Create prompt for filename suggestions based on content
    prompt = f"""Based on the following file content, suggest 5 better filenames for both the original file and its summary file.

Original filename: {input_file.name}
Content excerpt:
{content_excerpt}

Please provide 5 filename suggestions for each file. The filenames should:
- Be descriptive and reflect the content
- Be valid filenames (no invalid characters like /, \\, :, *, ?, ", <, >, |)
- Be concise but meaningful
- Preserve the original file extension ({input_file.suffix}) for the original file
- Use .md extension for the output file

Format your response as JSON:
{{
  "original": ["filename1{input_file.suffix}", "filename2{input_file.suffix}", "filename3{input_file.suffix}", "filename4{input_file.suffix}", "filename5{input_file.suffix}"],
  "output": ["filename1.md", "filename2.md", "filename3.md", "filename4.md", "filename5.md"]
}}

If you cannot format as JSON, provide a numbered list:
Original file suggestions:
1. filename1{input_file.suffix}
2. filename2{input_file.suffix}
3. filename3{input_file.suffix}
4. filename4{input_file.suffix}
5. filename5{input_file.suffix}

Output file suggestions:
1. filename1.md
2. filename2.md
3. filename3.md
4. filename4.md
5. filename5.md
"""
    
    try:
        response = provider.generate(prompt, "", max_tokens=500, temperature=0.7)
        output_file = input_file.parent / output_base
        return _parse_filename_suggestions(response, input_file, output_file)
    except Exception:
        return {"original": [], "output": []}


def _extract_json_from_text(text: str) -> Optional[str]:
    """Extract the first complete JSON object from text by finding matching braces.
    
    Args:
        text: Text that may contain JSON.
    
    Returns:
        Extracted JSON string, or None if no valid JSON found.
    """
    # Find the first opening brace
    start_idx = text.find('{')
    if start_idx == -1:
        return None
    
    # Find the matching closing brace by counting braces
    brace_count = 0
    in_string = False
    escape_next = False
    
    for i in range(start_idx, len(text)):
        char = text[i]
        
        if escape_next:
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            continue
        
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Found matching closing brace
                    json_str = text[start_idx:i+1]
                    # Validate it's valid JSON
                    try:
                        json.loads(json_str)
                        return json_str
                    except json.JSONDecodeError:
                        return None
    
    return None


def _parse_filename_suggestions(
    response: str,
    input_file: Path,
    output_file: Path
) -> Dict[str, List[str]]:
    """Parse filename suggestions from LLM response.
    
    Args:
        response: LLM response text.
        input_file: Original input file path (for fallback).
        output_file: Output file path (for fallback).
    
    Returns:
        Dictionary with keys "original" and "output", each containing a list of up to 5 filename suggestions.
    """
    result = {"original": [], "output": []}
    input_ext = input_file.suffix
    output_ext = output_file.suffix
    
    # Try to parse as JSON first
    try:
        # Extract JSON object from response using robust method
        json_str = _extract_json_from_text(response)
        if json_str:
            data = json.loads(json_str)
            original_suggestions = data.get("original", [])
            output_suggestions = data.get("output", [])
            
            # Validate and clean suggestions
            for suggestion in original_suggestions[:5]:
                if isinstance(suggestion, str):
                    # Ensure extension is preserved
                    if not suggestion.endswith(input_ext):
                        suggestion = suggestion.rsplit(".", 1)[0] + input_ext
                    # Sanitize filename
                    suggestion = sanitize_filename(suggestion)
                    if suggestion:
                        result["original"].append(suggestion)
            
            for suggestion in output_suggestions[:5]:
                if isinstance(suggestion, str):
                    # Ensure extension is .md
                    if not suggestion.endswith(output_ext):
                        suggestion = suggestion.rsplit(".", 1)[0] + output_ext
                    # Sanitize filename
                    suggestion = sanitize_filename(suggestion)
                    if suggestion:
                        result["output"].append(suggestion)
            
            if len(result["original"]) > 0 and len(result["output"]) > 0:
                return result
    except (json.JSONDecodeError, KeyError):
        pass
    
    # Fallback: Parse numbered list format
    # Look for "Original file suggestions:" or similar patterns
    original_pattern = r'(?:original|input|source).*?file.*?suggestions?:?\s*\n((?:\d+[\.\)\-\s]+\s*[^\n]+\n?){1,5})'
    output_pattern = r'(?:output|summary).*?file.*?suggestions?:?\s*\n((?:\d+[\.\)\-\s]+\s*[^\n]+\n?){1,5})'
    
    original_match = re.search(original_pattern, response, re.IGNORECASE | re.DOTALL)
    output_match = re.search(output_pattern, response, re.IGNORECASE | re.DOTALL)
    
    if original_match:
        lines = original_match.group(1).strip().split('\n')
        for line in lines[:5]:
            # Extract filename after number and separator (., ), -, or space)
            match = re.match(r'\d+[\.\)\-\s]+\s*(.+)', line.strip())
            if match:
                filename = match.group(1).strip()
                # Remove any trailing punctuation that might be part of formatting
                filename = filename.rstrip('.,;:')
                if not filename.endswith(input_ext):
                    filename = filename.rsplit(".", 1)[0] + input_ext
                filename = sanitize_filename(filename)
                if filename:
                    result["original"].append(filename)
    
    if output_match:
        lines = output_match.group(1).strip().split('\n')
        for line in lines[:5]:
            # Extract filename after number and separator (., ), -, or space)
            match = re.match(r'\d+[\.\)\-\s]+\s*(.+)', line.strip())
            if match:
                filename = match.group(1).strip()
                # Remove any trailing punctuation that might be part of formatting
                filename = filename.rstrip('.,;:')
                if not filename.endswith(output_ext):
                    filename = filename.rsplit(".", 1)[0] + output_ext
                filename = sanitize_filename(filename)
                if filename:
                    result["output"].append(filename)
    
    # If we still don't have 5 suggestions, pad with original filenames
    while len(result["original"]) < 5:
        result["original"].append(input_file.name)
    while len(result["output"]) < 5:
        result["output"].append(output_file.name)
    
    return result

