"""LLM provider registry for dynamic provider lookup."""

from typing import Dict, Type, Any
from txtguy.llm.providers.base import BaseLLMProvider
from txtguy.llm.providers.lm_studio import LMStudioProvider
from txtguy.llm.providers.qwen import QwenProvider
from txtguy.llm.providers.openai import OpenAIProvider


class ProviderRegistry:
    """Registry for LLM providers."""
    
    _providers: Dict[str, Type[BaseLLMProvider]] = {
        "lm_studio": LMStudioProvider,
        "qwen": QwenProvider,
        "openai": OpenAIProvider,
    }
    
    @classmethod
    def get_provider(cls, provider_name: str, settings: Dict[str, Any]) -> BaseLLMProvider:
        """Get a provider instance by name.
        
        Args:
            provider_name: Name of the provider (e.g., 'lm_studio', 'qwen', 'openai').
            settings: Settings dictionary for the provider.
        
        Returns:
            Initialized provider instance.
        
        Raises:
            ValueError: If provider is not found or configuration is invalid.
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unsupported LLM provider: {provider_name}. "
                f"Supported providers: {available}"
            )
        
        provider_class = cls._providers[provider_name]
        provider = provider_class(settings)
        
        if not provider.validate_config():
            raise ValueError(
                f"Invalid configuration for {provider_name}. "
                "Please check your config file."
            )
        
        return provider
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseLLMProvider]) -> None:
        """Register a new provider.
        
        Args:
            name: Provider name.
            provider_class: Provider class (must inherit from BaseLLMProvider).
        """
        if not issubclass(provider_class, BaseLLMProvider):
            raise TypeError(f"{provider_class} must inherit from BaseLLMProvider")
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def list_providers(cls) -> list[str]:
        """List all registered provider names.
        
        Returns:
            List of provider names.
        """
        return list(cls._providers.keys())

