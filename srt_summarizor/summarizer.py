"""Main summarization orchestration logic."""

import re
from pathlib import Path
from typing import Optional, List, Dict
from srt_summarizor.parser import SubtitleParser
from srt_summarizor.config import Config
from srt_summarizor.llm.base import BaseLLMProvider
from srt_summarizor.llm.lm_studio import LMStudioProvider

# Language code to full name mapping
LANGUAGE_MAP: Dict[str, str] = {
    "en": "english",
    "zh": "chinese",
    "zh-cn": "chinese",
    "zh-tw": "traditional chinese",
    "es": "spanish",
    "fr": "french",
    "de": "german",
    "ja": "japanese",
    "ko": "korean",
    "ru": "russian",
    "pt": "portuguese",
    "it": "italian",
    "ar": "arabic",
    "hi": "hindi",
    "th": "thai",
    "vi": "vietnamese",
}


def get_language_name(lang_code: str) -> str:
    """Convert language code to full language name.
    
    Args:
        lang_code: Language code (e.g., 'en', 'zh') or full name.
    
    Returns:
        Full language name for use in prompts.
    """
    lang_code_lower = lang_code.lower()
    # If it's already a full name (not in map), return as is
    if lang_code_lower not in LANGUAGE_MAP:
        # Check if it's a reverse lookup (full name provided)
        for code, name in LANGUAGE_MAP.items():
            if name.lower() == lang_code_lower:
                return name
        # If not found, assume it's a full name and return capitalized
        return lang_code.lower()
    return LANGUAGE_MAP[lang_code_lower]


class Summarizer:
    """Orchestrates subtitle parsing and LLM summarization."""
    
    # Maximum content length per LLM call (characters)
    MAX_CONTENT_LENGTH = 10000
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize summarizer.
        
        Args:
            config: Configuration object. If None, loads default config.
        """
        self.config = config or Config()
        self.llm_provider: Optional[BaseLLMProvider] = None
    
    def _get_llm_provider(self, provider_name: Optional[str] = None) -> BaseLLMProvider:
        """Get LLM provider instance.
        
        Args:
            provider_name: Provider name. If None, uses default from config.
        
        Returns:
            LLM provider instance.
        
        Raises:
            ValueError: If provider is not supported or configuration is invalid.
        """
        provider_name = provider_name or self.config.get("llm_provider", "lm_studio")
        settings = self.config.get_llm_settings(provider_name)
        
        if provider_name == "lm_studio":
            provider = LMStudioProvider(settings)
        # Future providers can be added here:
        # elif provider_name == "openai":
        #     provider = OpenAIProvider(settings)
        # elif provider_name == "qwen":
        #     provider = QwenProvider(settings)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
        
        if not provider.validate_config():
            raise ValueError(
                f"Invalid configuration for {provider_name}. "
                "Please check your config file."
            )
        
        return provider
    
    def summarize_file(
        self,
        input_file: Path,
        output_file: Optional[Path] = None,
        prompt_template: Optional[str] = None,
        provider: Optional[str] = None,
        language: str = "en",
        extra_context: Optional[str] = None,
        **llm_kwargs
    ) -> Path:
        """Summarize a single subtitle file.
        
        Args:
            input_file: Path to input subtitle file.
            output_file: Path to output markdown file. If None, auto-generates.
            prompt_template: Prompt template name. If None, uses default.
            provider: LLM provider name. If None, uses default from config.
            **llm_kwargs: Additional arguments for LLM (temperature, max_tokens, etc.)
        
        Returns:
            Path to output file.
        
        Raises:
            FileNotFoundError: If input file doesn't exist.
            ValueError: If summarization fails.
        """
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Get LLM provider
        if not self.llm_provider or provider:
            self.llm_provider = self._get_llm_provider(provider)
        
        # Parse subtitle file
        try:
            content = SubtitleParser.extract_text(input_file)
        except Exception as e:
            raise ValueError(f"Failed to parse subtitle file: {e}") from e
        
        if not content.strip():
            raise ValueError("Subtitle file is empty or contains no text")
        
        # Get prompt template
        try:
            prompt = self.config.get_prompt_template(prompt_template)
        except ValueError as e:
            raise ValueError(f"Prompt template error: {e}") from e
        
        # Generate summary
        try:
            summary = self._generate_summary(content, prompt, language=language, extra_context=extra_context, **llm_kwargs)
        except Exception as e:
            raise ValueError(f"Failed to generate summary: {e}") from e
        
        # Clean thinking content from summary
        summary = self._clean_thinking_content(summary)
        
        # Determine output path
        if output_file is None:
            output_file = self.config.get_output_path(input_file)
        else:
            output_file = Path(output_file)
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write markdown file
        self._write_markdown(output_file, input_file, summary)
        
        return output_file
    
    def summarize_files(
        self,
        input_files: List[Path],
        output_dir: Optional[Path] = None,
        prompt_template: Optional[str] = None,
        provider: Optional[str] = None,
        language: str = "en",
        extra_context: Optional[str] = None,
        **llm_kwargs
    ) -> List[Path]:
        """Summarize multiple subtitle files.
        
        Args:
            input_files: List of input subtitle file paths.
            output_dir: Output directory. If None, uses config default or input file directory.
            prompt_template: Prompt template name. If None, uses default.
            provider: LLM provider name. If None, uses default from config.
            **llm_kwargs: Additional arguments for LLM.
        
        Returns:
            List of output file paths.
        """
        output_files = []
        
        for input_file in input_files:
            output_file = None
            if output_dir:
                output_file = output_dir / f"{input_file.stem}.md"
            
            try:
                result = self.summarize_file(
                    input_file,
                    output_file=output_file,
                    prompt_template=prompt_template,
                    provider=provider,
                    language=language,
                    extra_context=extra_context,
                    **llm_kwargs
                )
                output_files.append(result)
            except Exception as e:
                # Continue with other files even if one fails
                print(f"Error processing {input_file}: {e}")
                continue
        
        return output_files
    
    def _generate_summary(self, content: str, prompt: str, language: str = "en", extra_context: Optional[str] = None, **kwargs) -> str:
        """Generate summary using LLM.
        
        Args:
            content: Subtitle content.
            prompt: Prompt template.
            language: Language code for the summary (default: en).
            extra_context: Additional context to help with summarization.
            **kwargs: Additional LLM arguments.
        
        Returns:
            Generated summary.
        """
        # Convert language code to full name for prompt
        language_name = get_language_name(language)
        # Add language instruction to prompt
        language_instruction = f"\n\nIMPORTANT: Write the summary in {language_name}. Do not include any thinking process, reasoning, or meta-commentary. Only provide the final summary."
        enhanced_prompt = prompt + language_instruction
        
        # Add extra context if provided
        if extra_context:
            enhanced_prompt += f"\n\nAdditional Context:\n{extra_context}\n"
        
        # Handle large content by chunking if needed
        if len(content) > self.MAX_CONTENT_LENGTH:
            return self._generate_summary_chunked(content, enhanced_prompt, language=language, extra_context=extra_context, **kwargs)
        else:
            return self.llm_provider.generate(enhanced_prompt, content, **kwargs)
    
    def _generate_summary_chunked(self, content: str, prompt: str, language: str = "en", extra_context: Optional[str] = None, **kwargs) -> str:
        """Generate summary for large content by chunking.
        
        Args:
            content: Subtitle content.
            prompt: Prompt template.
            language: Language code for the summary.
            extra_context: Additional context to help with summarization.
            **kwargs: Additional LLM arguments.
        
        Returns:
            Combined summary from all chunks.
        """
        # Convert language code to full name for prompt
        language_name = get_language_name(language)
        # Split content into chunks
        chunks = self._chunk_content(content)
        summaries = []
        
        # Add context to chunk prompt if provided
        context_suffix = f"\n\nAdditional Context:\n{extra_context}\n" if extra_context else ""
        
        for i, chunk in enumerate(chunks):
            chunk_prompt = (
                f"This is chunk {i+1} of {len(chunks)}. "
                f"Provide a summary focusing on the key points:\n\n{prompt}{context_suffix}"
            )
            summary = self.llm_provider.generate(chunk_prompt, chunk, **kwargs)
            summary = self._clean_thinking_content(summary)
            summaries.append(summary)
        
        # Combine summaries
        if len(summaries) > 1:
            combined_content = "\n\n".join(summaries)
            context_note = f"\n\nNote: The following context applies to all parts: {extra_context}\n" if extra_context else ""
            final_prompt = (
                f"The following are summaries of different parts of a subtitle file. "
                f"Please combine them into a single coherent summary in {language_name}. "
                f"Do not include any thinking process or reasoning - only the final summary.{context_note}\n\n"
                "{content}"
            )
            result = self.llm_provider.generate(final_prompt, combined_content, **kwargs)
            return self._clean_thinking_content(result)
        else:
            return summaries[0] if summaries else ""
    
    def _chunk_content(self, content: str) -> List[str]:
        """Split content into chunks.
        
        Args:
            content: Content to chunk.
        
        Returns:
            List of content chunks.
        """
        chunks = []
        lines = content.split("\n")
        current_chunk = []
        current_length = 0
        
        for line in lines:
            line_length = len(line)
            if current_length + line_length > self.MAX_CONTENT_LENGTH and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_length = line_length
            else:
                current_chunk.append(line)
                current_length += line_length + 1  # +1 for newline
        
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        
        return chunks
    
    def _clean_thinking_content(self, text: str) -> str:
        """Remove thinking/reasoning content from LLM response.
        
        Args:
            text: Text that may contain thinking content.
        
        Returns:
            Cleaned text without thinking content.
        """
        # Remove content in <think> tags (with flexible whitespace and attributes)
        # Run multiple passes to catch all variations and edge cases
        for _ in range(3):  # Multiple passes to handle nested or overlapping tags
            # Handle both opening and closing tags with optional whitespace/attributes
            text = re.sub(r'<redacted_reasoning\s*[^>]*>.*?</redacted_reasoning\s*>', '', text, flags=re.DOTALL | re.IGNORECASE)
            # Also remove any unclosed <think> tags and everything after them
            text = re.sub(r'<redacted_reasoning\s*[^>]*>.*', '', text, flags=re.DOTALL | re.IGNORECASE)
            # Remove any remaining closing tags without opening tags (with optional whitespace)
            text = re.sub(r'</redacted_reasoning\s*>', '', text, flags=re.IGNORECASE)
            # Remove any standalone opening tags (with optional whitespace)
            text = re.sub(r'<redacted_reasoning\s*[^>]*>', '', text, flags=re.IGNORECASE)
        
        # Remove content in <thinking> tags
        for _ in range(3):
            text = re.sub(r'<thinking\s*[^>]*>.*?</thinking\s*>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<thinking\s*[^>]*>.*', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'</thinking\s*>', '', text, flags=re.IGNORECASE)
            text = re.sub(r'<thinking\s*[^>]*>', '', text, flags=re.IGNORECASE)
        
        # Remove content in <reasoning> tags
        for _ in range(3):
            text = re.sub(r'<reasoning\s*[^>]*>.*?</reasoning\s*>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<reasoning\s*[^>]*>.*', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'</reasoning\s*>', '', text, flags=re.IGNORECASE)
            text = re.sub(r'<reasoning\s*[^>]*>', '', text, flags=re.IGNORECASE)
        
        # Remove content in <!-- thinking --> comments
        text = re.sub(r'<!--\s*thinking.*?-->', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove lines that start with "Okay, I need to" or similar thinking patterns
        lines = text.split('\n')
        cleaned_lines = []
        skip_thinking = False
        
        for line in lines:
            # Skip lines that look like thinking/reasoning
            if re.match(r'^(Okay|Let me|I need to|I should|First|Let\'s|I\'ll|I will)', line, re.IGNORECASE):
                if 'summary' not in line.lower() and 'conclusion' not in line.lower():
                    skip_thinking = True
                    continue
            
            # Stop skipping when we hit actual content
            if skip_thinking and (line.strip().startswith('#') or line.strip().startswith('**') or len(line.strip()) > 50):
                skip_thinking = False
            
            if not skip_thinking:
                cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        
        # Clean up multiple blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _write_markdown(self, output_file: Path, input_file: Path, summary: str) -> None:
        """Write summary to markdown file.
        
        Args:
            output_file: Output file path.
            input_file: Original input file path (for metadata).
            summary: Summary text.
        """
        markdown_content = f"""# Summary: {input_file.name}

**Source File:** `{input_file.name}`

---

{summary}
"""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

