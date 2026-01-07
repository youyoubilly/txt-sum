"""Main summarization orchestration logic.

This module provides backward compatibility by wrapping the new
app-layer orchestrator. For new code, prefer importing from
txt_sum.app.summarize directly.
"""

from pathlib import Path
from typing import Optional, List

from txt_sum.config import Config
from txt_sum.app.summarize import SummarizerOrchestrator
from txt_sum.domain.errors import ContentTooLongError


class Summarizer:
    """Orchestrates text file parsing and LLM summarization.
    
    This is a backward-compatibility wrapper around SummarizerOrchestrator.
    For new code, use txt_sum.app.summarize.SummarizerOrchestrator directly.
    """
    
    # Maximum content length per LLM call (characters)
    MAX_CONTENT_LENGTH = 10000
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize summarizer.
        
        Args:
            config: Configuration object. If None, loads default config.
        """
        self.config = config or Config()
        self._orchestrator = SummarizerOrchestrator(self.config)
        self.llm_provider = None  # For backward compatibility
        self.prompt_manager = self._orchestrator.prompt_manager
        self.max_text_length = self._orchestrator.max_text_length
    
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
            ValueError: If summarization fails.
        """
        try:
            return self._orchestrator.summarize_file(
                input_file=input_file,
                output_file=output_file,
                prompt_template=prompt_template,
                provider=provider,
                language=language,
                extra_context=extra_context,
                full_context=full_context,
                force_text=force_text,
                **llm_kwargs
            )
        except ContentTooLongError:
            # Return None for backward compatibility with CLI expectations
            return None
        except Exception as e:
            # Re-raise as ValueError for backward compatibility
            if not isinstance(e, (FileNotFoundError, ValueError)):
                raise ValueError(str(e)) from e
            raise
    
    def summarize_files(
        self,
        input_files: List[Path],
        output_dir: Optional[Path] = None,
        prompt_template: Optional[str] = None,
        provider: Optional[str] = None,
        language: str = "en",
        extra_context: Optional[str] = None,
        full_context: bool = False,
        force_text: bool = False,
        **llm_kwargs
    ) -> List[Path]:
        """Summarize multiple text files.
        
        Args:
            input_files: List of input text file paths.
            output_dir: Output directory. If None, uses config default or input file directory.
            prompt_template: Prompt template name. If None, uses default.
            provider: LLM provider name. If None, uses default from config.
            language: Language code for the summary.
            extra_context: Additional context to help with summarization.
            full_context: If True, preserve timestamps and formatting.
            force_text: If True, attempt to process unknown file types.
            **llm_kwargs: Additional arguments for LLM.
        
        Returns:
            List of output file paths (skipped files are not included).
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
                    full_context=full_context,
                    force_text=force_text,
                    **llm_kwargs
                )
                if result is not None:
                    output_files.append(result)
            except Exception as e:
                # Continue with other files even if one fails
                print(f"Error processing {input_file}: {e}")
                continue
        
        return output_files
