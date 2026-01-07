"""Configuration management for txt-sum."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Manages configuration for txt-sum."""
    
    CONFIG_DIR = Path.home() / ".txt-sum"
    CONFIG_FILE = CONFIG_DIR / "config.yaml"
    PROMPTS_FILE = CONFIG_DIR / "prompts.yaml"
    
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
        "default_prompt_template": "default",
        "max_text_length": 100000,
        "prompts_file": str(PROMPTS_FILE),
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
    
    def get_prompts_file(self) -> Path:
        """Get path to prompts.yaml file.
        
        Returns:
            Path to prompts file.
        """
        prompts_path = self.get("prompts_file", str(self.PROMPTS_FILE))
        return Path(prompts_path).expanduser()
    
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
        
        # Also initialize prompts.yaml if it doesn't exist
        from txt_sum.prompts.manager import PromptManager
        prompts_file = config.get_prompts_file()
        if not prompts_file.exists():
            prompt_manager = PromptManager(prompts_file)
            prompt_manager.init_default_prompts()
        
        return config.config_path

