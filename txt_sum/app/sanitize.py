"""LLM response sanitization - remove thinking tags and meta-content."""

import re


def sanitize_llm_response(text: str) -> str:
    """Remove thinking/reasoning content from LLM response.
    
    Many LLMs include reasoning or thinking process in special tags like
    <think>, <thinking>, <reasoning>, or similar. This function removes
    those tags and their content to provide clean summaries.
    
    Args:
        text: Text that may contain thinking content.
    
    Returns:
        Cleaned text without thinking content.
    """
    # Remove content in various thinking-related tags
    # Run multiple passes to catch nested or overlapping tags
    for _ in range(3):
        # <think> tags
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # <redacted_reasoning> tags (with optional attributes)
        text = re.sub(
            r'<redacted_reasoning[^>]*>.*?</redacted_reasoning[^>]*>',
            '',
            text,
            flags=re.DOTALL | re.IGNORECASE
        )
        text = re.sub(r'<redacted_reasoning[^>]*>.*', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # <thinking> tags (with optional attributes)
        text = re.sub(
            r'<thinking\s*[^>]*>.*?</thinking\s*>',
            '',
            text,
            flags=re.DOTALL | re.IGNORECASE
        )
        text = re.sub(r'<thinking\s*[^>]*>.*', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # <reasoning> tags (with optional attributes)
        text = re.sub(
            r'<reasoning\s*[^>]*>.*?</reasoning\s*>',
            '',
            text,
            flags=re.DOTALL | re.IGNORECASE
        )
        text = re.sub(r'<reasoning\s*[^>]*>.*', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove orphaned closing tags
        text = re.sub(r'</think>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</thinking\s*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</reasoning\s*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</redacted_reasoning\s*>', '', text, flags=re.IGNORECASE)
        
        # Remove orphaned opening tags
        text = re.sub(r'<thinking\s*[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<reasoning\s*[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<redacted_reasoning[^>]*>', '', text, flags=re.IGNORECASE)
    
    # Remove HTML comment-style thinking
    text = re.sub(r'<!--\s*thinking.*?-->', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove lines that look like meta-thinking patterns
    lines = text.split('\n')
    cleaned_lines = []
    skip_thinking = False
    
    for line in lines:
        # Skip lines that start with common thinking patterns
        if re.match(
            r'^(Okay|Let me|I need to|I should|First|Let\'s|I\'ll|I will)\b',
            line,
            re.IGNORECASE
        ):
            # Unless it's about the actual summary/conclusion
            if 'summary' not in line.lower() and 'conclusion' not in line.lower():
                skip_thinking = True
                continue
        
        # Stop skipping when we hit actual content markers
        if skip_thinking and (
            line.strip().startswith('#') or
            line.strip().startswith('**') or
            len(line.strip()) > 50
        ):
            skip_thinking = False
        
        if not skip_thinking:
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Remove standalone placeholder words
    placeholder_patterns = [
        r'^\s*space\s*$',
        r'^\s*thinking\s*$',
        r'^\s*reasoning\s*$',
        r'^\s*\.\s*$',
        r'^\s*\.\.\.\s*$',
    ]
    
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        should_skip = False
        for pattern in placeholder_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                should_skip = True
                break
        if not should_skip:
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Clean up multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

