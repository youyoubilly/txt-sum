"""Prompt template manager."""

import yaml
from pathlib import Path
from typing import Dict, Optional
from txt_sum.prompts.defaults import DEFAULT_PROMPTS


class PromptManager:
    """Manages prompt templates loaded from YAML file."""
    
    def __init__(self, prompts_file: Optional[Path] = None):
        """Initialize prompt manager.
        
        Args:
            prompts_file: Path to prompts.yaml file. If None, uses default location.
        """
        if prompts_file is None:
            from txt_sum.config import Config
            config = Config()
            prompts_file = config.get_prompts_file()
        
        self.prompts_file = Path(prompts_file)
        self._prompts: Dict[str, str] = {}
        self.load()
    
    def load(self) -> None:
        """Load prompts from YAML file or use defaults."""
        if self.prompts_file.exists():
            try:
                with open(self.prompts_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    templates = data.get("templates", {})
                    self._prompts = templates.copy()
            except Exception:
                # If loading fails, use defaults
                self._prompts = DEFAULT_PROMPTS.copy()
        else:
            # Use defaults if file doesn't exist
            self._prompts = DEFAULT_PROMPTS.copy()
    
    def get_prompt(self, template_name: Optional[str] = None) -> str:
        """Get a prompt template.
        
        Args:
            template_name: Template name. If None, uses "default".
        
        Returns:
            Prompt template string.
        
        Raises:
            ValueError: If template not found.
        """
        template_name = template_name or "default"
        prompt = self._prompts.get(template_name)
        if not prompt:
            raise ValueError(f"Prompt template '{template_name}' not found")
        return prompt
    
    def list_prompts(self) -> list[str]:
        """List all available prompt template names.
        
        Returns:
            List of template names.
        """
        return list(self._prompts.keys())
    
    def save_prompt(self, template_name: str, prompt: str) -> None:
        """Save a prompt template to the YAML file.
        
        Args:
            template_name: Name of the template.
            prompt: Prompt template string.
        """
        self._prompts[template_name] = prompt
        self._save_to_file()
    
    def _save_to_file(self) -> None:
        """Save prompts to YAML file."""
        self.prompts_file.parent.mkdir(parents=True, exist_ok=True)
        data = {"templates": self._prompts}
        with open(self.prompts_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    def init_default_prompts(self) -> Path:
        """Initialize prompts.yaml file with default templates.
        
        Returns:
            Path to created prompts file.
        """
        self._prompts = DEFAULT_PROMPTS.copy()
        self._save_to_file()
        return self.prompts_file

