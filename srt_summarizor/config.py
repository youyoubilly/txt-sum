"""Configuration management for SRT Summarizor."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Manages configuration for SRT Summarizor."""
    
    CONFIG_DIR = Path.home() / ".srt-summarizor"
    CONFIG_FILE = CONFIG_DIR / "config.yaml"
    
    DEFAULT_CONFIG = {
        "default_output_path": "~/Documents/summaries",
        "llm_provider": "lm_studio",
        "llm_settings": {
            "lm_studio": {
                "base_url": "http://localhost:1234/v1",
                "api_key": "",
                "model": "",
            },
            "openai": {
                "api_key": "",
                "model": "gpt-3.5-turbo",
            },
            "qwen": {
                "api_key": "",
                "model": "qwen-turbo",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            },
        },
        "prompt_templates": {
            "default": (
                "Please summarize the following subtitle content in a clear and concise manner.\n"
                "Focus on the main themes, key events, and important dialogue.\n\n"
                "Subtitle content:\n{content}"
            ),
            "detailed": (
                "Provide a detailed summary of the following subtitle content with:\n"
                "1. Overview\n"
                "2. Key Themes\n"
                "3. Important Events\n"
                "4. Character Interactions\n\n"
                "Subtitle content:\n{content}"
            ),
            "brief": (
                "Create a brief summary (2-3 sentences) of the following subtitle content:\n\n"
                "{content}"
            ),
        },
        "default_prompt_template": "default",
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager.
        
        Args:
            config_path: Optional custom path to config file. If None, uses default.
        """
        self.config_path = config_path or self.CONFIG_FILE
        self._config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary.
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config = yaml.safe_load(f) or {}
            except Exception as e:
                raise ValueError(f"Failed to load config from {self.config_path}: {e}")
        else:
            self._config = self.DEFAULT_CONFIG.copy()
        
        # Merge with defaults to ensure all keys exist
        self._merge_defaults()
        return self._config
    
    def save(self) -> None:
        """Save configuration to file."""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
    
    def _merge_defaults(self) -> None:
        """Merge current config with defaults to ensure all keys exist."""
        def merge_dict(base: Dict, updates: Dict) -> Dict:
            result = base.copy()
            for key, value in updates.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dict(result[key], value)
                else:
                    result[key] = value
            return result
        
        self._config = merge_dict(self.DEFAULT_CONFIG.copy(), self._config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., "llm_settings.lm_studio.base_url")
            default: Default value if key not found.
        
        Returns:
            Configuration value.
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set.
        """
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def get_output_path(self, input_file: Optional[Path] = None) -> Path:
        """Get output path for a file.
        
        Args:
            input_file: Optional input file path to derive output name from.
        
        Returns:
            Output path.
        """
        default_path = Path(self.get("default_output_path", "~/Documents/summaries")).expanduser()
        
        if input_file:
            # If input file provided, use same directory with .md extension
            output_file = input_file.with_suffix(".md")
            return output_file
        
        return default_path
    
    def get_llm_settings(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get LLM settings for a provider.
        
        Args:
            provider: Provider name. If None, uses default provider.
        
        Returns:
            LLM settings dictionary.
        """
        provider = provider or self.get("llm_provider", "lm_studio")
        settings = self.get(f"llm_settings.{provider}", {})
        return settings.copy()
    
    def get_prompt_template(self, template_name: Optional[str] = None) -> str:
        """Get a prompt template.
        
        Args:
            template_name: Template name. If None, uses default template.
        
        Returns:
            Prompt template string.
        """
        template_name = template_name or self.get("default_prompt_template", "default")
        template = self.get(f"prompt_templates.{template_name}")
        if not template:
            raise ValueError(f"Prompt template '{template_name}' not found")
        return template
    
    @classmethod
    def init_config(cls, config_path: Optional[Path] = None) -> Path:
        """Initialize configuration file with defaults.
        
        Args:
            config_path: Optional custom path. If None, uses default.
        
        Returns:
            Path to created config file.
        """
        config = cls(config_path)
        config.save()
        return config.config_path

