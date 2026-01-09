"""Base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, settings: Dict[str, Any]):
        """Initialize LLM provider.
        
        Args:
            settings: Provider-specific settings dictionary.
        """
        self.settings = settings
    
    @abstractmethod
    def generate(self, prompt: str, content: str, **kwargs) -> str:
        """Generate summary using LLM.
        
        Args:
            prompt: Prompt template.
            content: Subtitle content to summarize.
            **kwargs: Additional arguments for the LLM call.
        
        Returns:
            Generated summary text.
        
        Raises:
            ValueError: If configuration is invalid.
            ConnectionError: If connection to LLM service fails.
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate provider configuration.
        
        Returns:
            True if configuration is valid, False otherwise.
        """
        pass
    
    def format_prompt(self, prompt_template: str, content: str) -> str:
        """Format prompt template with content.
        
        Args:
            prompt_template: Prompt template with {content} placeholder.
            content: Content to insert into template.
        
        Returns:
            Formatted prompt string.
        """
        return prompt_template.format(content=content)

