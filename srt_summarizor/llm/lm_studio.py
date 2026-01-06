"""LM Studio LLM provider implementation."""

import requests
from typing import Dict, Any, Optional
from srt_summarizor.llm.base import BaseLLMProvider


class LMStudioProvider(BaseLLMProvider):
    """LM Studio provider using OpenAI-compatible API."""
    
    def __init__(self, settings: Dict[str, Any]):
        """Initialize LM Studio provider.
        
        Args:
            settings: Settings dictionary with 'base_url', 'api_key', 'model' keys.
        """
        super().__init__(settings)
        self.base_url = settings.get("base_url", "http://localhost:1234/v1")
        self.api_key = settings.get("api_key", "")
        self.model = settings.get("model", "")
    
    def validate_config(self) -> bool:
        """Validate LM Studio configuration.
        
        Returns:
            True if configuration is valid.
        """
        if not self.base_url:
            return False
        # Try to connect to the server
        try:
            response = requests.get(
                f"{self.base_url.rstrip('/v1')}/v1/models",
                headers=self._get_headers(),
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def generate(self, prompt: str, content: str, **kwargs) -> str:
        """Generate summary using LM Studio.
        
        Args:
            prompt: Prompt template.
            content: Subtitle content to summarize.
            **kwargs: Additional arguments (max_tokens, temperature, etc.)
        
        Returns:
            Generated summary text.
        
        Raises:
            ConnectionError: If connection to LM Studio fails.
            ValueError: If API request fails.
        """
        full_prompt = self.format_prompt(prompt, content)
        
        # Use chat completions endpoint (OpenAI-compatible)
        url = f"{self.base_url.rstrip('/v1')}/v1/chat/completions"
        
        payload = {
            "model": self.model or self._get_default_model(),
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=kwargs.get("timeout", 120)
            )
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                raise ValueError("Unexpected response format from LM Studio API")
        
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Failed to connect to LM Studio at {self.base_url}. "
                "Make sure LM Studio is running and the server is started."
            ) from e
        except requests.exceptions.HTTPError as e:
            raise ValueError(f"LM Studio API error: {e}") from e
        except requests.exceptions.Timeout:
            raise ConnectionError("Request to LM Studio timed out") from None
        except Exception as e:
            raise ValueError(f"Unexpected error calling LM Studio: {e}") from e
    
    def _get_default_model(self) -> str:
        """Get default model from available models.
        
        Returns:
            Model name, or empty string if none available.
        """
        try:
            url = f"{self.base_url.rstrip('/v1')}/v1/models"
            response = requests.get(url, headers=self._get_headers(), timeout=5)
            if response.status_code == 200:
                models = response.json()
                if "data" in models and len(models["data"]) > 0:
                    return models["data"][0]["id"]
        except Exception:
            pass
        return ""
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests.
        
        Returns:
            Headers dictionary.
        """
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

