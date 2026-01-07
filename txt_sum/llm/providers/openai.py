"""OpenAI LLM provider implementation."""

import requests
from typing import Dict, Any
from txt_sum.llm.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider using OpenAI API."""
    
    def __init__(self, settings: Dict[str, Any]):
        """Initialize OpenAI provider.
        
        Args:
            settings: Settings dictionary with 'api_key', 'model' keys.
        """
        super().__init__(settings)
        self.base_url = settings.get("base_url", "https://api.openai.com/v1")
        self.api_key = settings.get("api_key", "")
        self.model = settings.get("model", "gpt-3.5-turbo")
    
    def validate_config(self) -> bool:
        """Validate OpenAI configuration.
        
        Returns:
            True if configuration is valid.
        """
        if not self.api_key:
            return False
        if not self.model:
            return False
        # Basic validation - we have the required fields
        return True
    
    def generate(self, prompt: str, content: str, **kwargs) -> str:
        """Generate summary using OpenAI.
        
        Args:
            prompt: Prompt template.
            content: Subtitle content to summarize.
            **kwargs: Additional arguments (max_tokens, temperature, etc.)
        
        Returns:
            Generated summary text.
        
        Raises:
            ConnectionError: If connection to OpenAI API fails.
            ValueError: If API request fails.
        """
        full_prompt = self.format_prompt(prompt, content)
        
        # Use chat completions endpoint
        url = f"{self.base_url.rstrip('/v1')}/v1/chat/completions"
        
        payload = {
            "model": self.model,
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
                raise ValueError("Unexpected response format from OpenAI API")
        
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Failed to connect to OpenAI API at {self.base_url}. "
                "Please check your internet connection and API configuration."
            ) from e
        except requests.exceptions.HTTPError as e:
            error_msg = f"OpenAI API error: {e}"
            if response.status_code == 401:
                error_msg += " Please check your API key."
            elif response.status_code == 404:
                error_msg += " Please check your model name."
            elif response.status_code == 429:
                error_msg += " Rate limit exceeded. Please try again later."
            raise ValueError(error_msg) from e
        except requests.exceptions.Timeout:
            raise ConnectionError("Request to OpenAI API timed out") from None
        except Exception as e:
            raise ValueError(f"Unexpected error calling OpenAI API: {e}") from e
    
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

