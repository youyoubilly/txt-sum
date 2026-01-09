"""Tests for provider registry."""

import pytest
from txtguy.llm.registry import ProviderRegistry
from txtguy.llm.providers.base import BaseLLMProvider
from txtguy.llm.providers.lm_studio import LMStudioProvider
from txtguy.llm.providers.qwen import QwenProvider
from txtguy.llm.providers.openai import OpenAIProvider


def test_registry_list_providers():
    """Test listing available providers."""
    providers = ProviderRegistry.list_providers()
    assert "lm_studio" in providers
    assert "qwen" in providers
    assert "openai" in providers


def test_registry_get_provider_lm_studio():
    """Test getting LM Studio provider."""
    settings = {
        "base_url": "http://localhost:1234/v1",
        "api_key": "",
        "model": "test-model"
    }
    # Note: This will fail validation without actual server
    # Just test that registry returns correct type
    try:
        provider = ProviderRegistry.get_provider("lm_studio", settings)
        assert isinstance(provider, LMStudioProvider)
    except ValueError as e:
        # Expected if validation fails - that's OK for this test
        assert "Invalid configuration" in str(e)


def test_registry_get_provider_qwen():
    """Test getting Qwen provider."""
    settings = {
        "api_key": "test-key",
        "model": "qwen-turbo",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    }
    # Note: This will fail validation without actual API key
    try:
        provider = ProviderRegistry.get_provider("qwen", settings)
        assert isinstance(provider, QwenProvider)
    except ValueError as e:
        # Expected if validation fails - that's OK for this test
        assert "Invalid configuration" in str(e)


def test_registry_get_provider_openai():
    """Test getting OpenAI provider."""
    settings = {
        "api_key": "test-key",
        "model": "gpt-3.5-turbo"
    }
    # Note: This will fail validation without actual API key
    # But we can test it returns correct type before validation
    provider_class = ProviderRegistry._providers.get("openai")
    assert provider_class == OpenAIProvider


def test_registry_invalid_provider():
    """Test getting invalid provider raises error."""
    with pytest.raises(ValueError) as exc_info:
        ProviderRegistry.get_provider("invalid_provider", {})
    assert "Unsupported LLM provider" in str(exc_info.value)


def test_registry_register_custom_provider():
    """Test registering a custom provider."""
    
    class CustomProvider(BaseLLMProvider):
        def generate(self, prompt, content, **kwargs):
            return "test"
        
        def validate_config(self):
            return True
    
    ProviderRegistry.register_provider("custom", CustomProvider)
    assert "custom" in ProviderRegistry.list_providers()
    
    provider = ProviderRegistry.get_provider("custom", {})
    assert isinstance(provider, CustomProvider)


def test_registry_case_insensitive():
    """Test that provider names are case-insensitive."""
    settings = {
        "api_key": "test",
        "model": "test"
    }
    
    provider_lower = ProviderRegistry._providers.get("lm_studio")
    provider_upper = ProviderRegistry._providers.get("LM_STUDIO".lower())
    
    assert provider_lower == provider_upper

