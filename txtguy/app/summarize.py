"""Main summarization orchestration logic."""

from pathlib import Path
from typing import Optional, Dict

from txtguy.config import Config
from txtguy.parser import SubtitleParser
from txtguy.llm.registry import ProviderRegistry
from txtguy.llm.providers.base import BaseLLMProvider
from txtguy.prompts.manager import PromptManager
from txtguy.app.chunking import chunk_content
from txtguy.app.sanitize import sanitize_llm_response
from txtguy.app.output import write_markdown_summary
from txtguy.domain.errors import ContentTooLongError, ParseError, ProviderError


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
        # If not found, assume it's a full name and return as-is
        return lang_code.lower()
    return LANGUAGE_MAP[lang_code_lower]


class SummarizerOrchestrator:
    """Orchestrates the summarization workflow."""
    
    # Maximum content length per LLM call (characters)
    MAX_CONTENT_LENGTH = 10000
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize orchestrator.
        
        Args:
            config: Configuration object. If None, loads default config.
        """
        self.config = config or Config()
        self.llm_provider: Optional[BaseLLMProvider] = None
        self.prompt_manager = PromptManager(self.config.get_prompts_file())
        self.max_text_length = self.config.get("max_text_length", 100000)
    
    def summarize_file(
        self,
        input_file: Path,
        output_file: Optional[Path] = None,
        prompt_template: Optional[str] = None,
        provider: Optional[str] = None,
        language: str = "en",
        extra_context: Optional[str] = None,
        full_context: bool = False,
        force_text: bool = False,
        **llm_kwargs
    ) -> Optional[Path]:
        """Summarize a single text file.
        
        Args:
            input_file: Path to input text file.
            output_file: Path to output markdown file. If None, auto-generates.
            prompt_template: Prompt template name. If None, uses default.
            provider: LLM provider name. If None, uses default from config.
            language: Language code for the summary.
            extra_context: Additional context to help with summarization.
            full_context: If True, preserve timestamps and formatting.
            force_text: If True, attempt to process unknown file types.
            **llm_kwargs: Additional arguments for LLM (temperature, max_tokens, etc.)
        
        Returns:
            Path to output file, or None if file was skipped due to length.
        
        Raises:
            FileNotFoundError: If input file doesn't exist.
            ParseError: If file parsing fails.
            ProviderError: If LLM provider fails.
            ContentTooLongError: If content exceeds maximum length.
        """
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Get LLM provider
        if not self.llm_provider or provider:
            try:
                provider_name = provider or self.config.get("llm_provider", "lm_studio")
                settings = self.config.get_llm_settings(provider_name)
                self.llm_provider = ProviderRegistry.get_provider(provider_name, settings)
            except Exception as e:
                raise ProviderError(f"Failed to initialize LLM provider: {e}") from e
        
        # Parse text file
        try:
            content = SubtitleParser.extract_text(
                input_file,
                full_context=full_context,
                force_text=force_text
            )
        except Exception as e:
            raise ParseError(f"Failed to parse file {input_file.name}: {e}") from e
        
        if not content.strip():
            raise ParseError(f"File is empty or contains no text: {input_file.name}")
        
        # Check text length
        if len(content) > self.max_text_length:
            raise ContentTooLongError(
                content_length=len(content),
                max_length=self.max_text_length,
                file_name=input_file.name
            )
        
        # Get prompt template
        try:
            # Support category:template format (e.g., "short:default")
            if prompt_template and ":" in prompt_template:
                category, template_in_category = prompt_template.split(":", 1)
                prompt = self.prompt_manager.get_prompt(
                    category=category,
                    template_in_category=template_in_category
                )
            else:
                prompt = self.prompt_manager.get_prompt(prompt_template)
        except ValueError as e:
            raise ParseError(f"Prompt template error: {e}") from e
        
        # Generate summary
        try:
            summary = self._generate_summary(
                content,
                prompt,
                language=language,
                extra_context=extra_context,
                **llm_kwargs
            )
        except Exception as e:
            raise ProviderError(f"Failed to generate summary: {e}") from e
        
        # Clean thinking content from summary
        summary = sanitize_llm_response(summary)
        
        # Determine output path
        if output_file is None:
            output_file = self.config.get_output_path(input_file)
        else:
            output_file = Path(output_file)
        
        # Write markdown file
        write_markdown_summary(output_file, input_file, summary)
        
        return output_file
    
    def _generate_summary(
        self,
        content: str,
        prompt: str,
        language: str = "en",
        extra_context: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate summary using LLM.
        
        Args:
            content: Text content.
            prompt: Prompt template.
            language: Language code for the summary (default: en).
            extra_context: Additional context to help with summarization.
            **kwargs: Additional LLM arguments.
        
        Returns:
            Generated summary.
        """
        # Convert language code to full name for prompt
        language_name = get_language_name(language)
        
        # Create strong language instruction at the beginning of the prompt
        if language.lower() != "en":
            language_instruction = (
                f"CRITICAL: You must write the entire summary in {language_name}. "
                f"All content, including headings, sections, paragraphs, and any text, must be in {language_name}. "
                f"Do not use English or any other language. Only use {language_name}. "
                "Do not include any thinking process, reasoning, or meta-commentary. "
                f"Only provide the final summary in {language_name}.\n\n"
            )
        else:
            language_instruction = (
                "Do not include any thinking process, reasoning, or meta-commentary. "
                "Only provide the final summary.\n\n"
            )
        
        # Place language instruction BEFORE the template prompt content
        enhanced_prompt = language_instruction + prompt
        
        # Add extra context if provided (only once, not duplicated in chunking)
        if extra_context:
            enhanced_prompt += f"\n\nAdditional Context:\n{extra_context}\n"
        
        # Handle large content by chunking if needed
        if len(content) > self.MAX_CONTENT_LENGTH:
            return self._generate_summary_chunked(
                content,
                enhanced_prompt,
                language_name,
                **kwargs
            )
        else:
            return self.llm_provider.generate(enhanced_prompt, content, **kwargs)
    
    def _generate_summary_chunked(
        self,
        content: str,
        enhanced_prompt: str,
        language_name: str,
        **kwargs
    ) -> str:
        """Generate summary for large content by chunking.
        
        Args:
            content: Text content.
            enhanced_prompt: Enhanced prompt with language and context already added.
            language_name: Full language name for final combination prompt.
            **kwargs: Additional LLM arguments.
        
        Returns:
            Combined summary from all chunks.
        """
        # Split content into chunks
        chunks = chunk_content(content, self.MAX_CONTENT_LENGTH)
        summaries = []
        
        # Generate summary for each chunk
        for i, chunk in enumerate(chunks):
            # Ensure language instruction is prominent in chunk prompts
            chunk_prompt = (
                f"This is chunk {i+1} of {len(chunks)}. "
                f"Provide a summary focusing on the key points:\n\n{enhanced_prompt}"
            )
            summary = self.llm_provider.generate(chunk_prompt, chunk, **kwargs)
            summary = sanitize_llm_response(summary)
            summaries.append(summary)
        
        # Combine summaries if we have multiple chunks
        if len(summaries) > 1:
            combined_content = "\n\n".join(summaries)
            # Create strong language instruction for final combination
            if language_name.lower() != "english":
                final_prompt = (
                    f"CRITICAL: You must write the entire combined summary in {language_name}. "
                    f"All content, including headings, sections, paragraphs, and any text, must be in {language_name}. "
                    f"Do not use English or any other language. Only use {language_name}.\n\n"
                    f"The following are summaries of different parts of a text file. "
                    f"Please combine them into a single coherent summary in {language_name}. "
                    "Do not include any thinking process, reasoning, or meta-commentary. "
                    "Only provide the final summary.\n\n"
                    "{content}"
                )
            else:
                final_prompt = (
                    f"The following are summaries of different parts of a text file. "
                    f"Please combine them into a single coherent summary. "
                    "Do not include any thinking process or reasoning - only the final summary.\n\n"
                    "{content}"
                )
            result = self.llm_provider.generate(final_prompt, combined_content, **kwargs)
            return sanitize_llm_response(result)
        else:
            return summaries[0] if summaries else ""

