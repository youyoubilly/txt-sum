"""Prompt template manager."""

import yaml
from pathlib import Path
from typing import Dict, Optional, List
from txtguy.prompts.defaults import DEFAULT_PROMPTS
from txtguy.prompts.categories import DEFAULT_CATEGORIES, LEGACY_DEFAULT_PROMPTS


class PromptManager:
    """Manages prompt templates loaded from YAML file with category support."""
    
    def __init__(self, templates_file: Optional[Path] = None):
        """Initialize prompt manager.
        
        Args:
            templates_file: Path to templates.yaml file. If None, uses default location.
        """
        if templates_file is None:
            from txtguy.config import Config
            config = Config()
            templates_file = config.get_templates_file()
        
        self.templates_file = Path(templates_file)
        self._categories: Dict[str, Dict[str, str]] = {}
        self._custom: Dict[str, str] = {}
        self._legacy_templates: Dict[str, str] = {}
        self.load()
    
    def load(self) -> None:
        """Load templates from YAML file or use defaults."""
        if self.templates_file.exists():
            try:
                with open(self.templates_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    
                    # Load new format with categories
                    if "categories" in data:
                        self._categories = data.get("categories", {})
                    else:
                        self._categories = {}
                    
                    # Load custom templates
                    self._custom = data.get("custom", {})
                    
                    # Load legacy format for backward compatibility
                    if "templates" in data and not self._categories:
                        self._legacy_templates = data.get("templates", {})
            except Exception:
                # If loading fails, use defaults
                self._categories = {}
                self._custom = {}
                self._legacy_templates = {}
        else:
            # Use defaults if file doesn't exist
            self._categories = {}
            self._custom = {}
            self._legacy_templates = {}
    
    def get_prompt(
        self, 
        template_name: Optional[str] = None,
        category: Optional[str] = None,
        template_in_category: Optional[str] = None
    ) -> str:
        """Get a prompt template.
        
        Args:
            template_name: Template name (for legacy or custom templates). If None, uses "default".
            category: Category name (e.g., "short", "long", "blog").
            template_in_category: Template name within category (e.g., "default", "concise").
                                 If None and category is provided, uses "default".
        
        Returns:
            Prompt template string.
        
        Raises:
            ValueError: If template not found.
        """
        # If category is provided, look in categories first
        if category:
            if category in self._categories:
                category_templates = self._categories[category]
                template_key = template_in_category or "default"
                if template_key in category_templates:
                    return category_templates[template_key]
                raise ValueError(f"Template '{template_key}' not found in category '{category}'")
            # Fall back to default categories if not in user's file
            if category in DEFAULT_CATEGORIES:
                category_templates = DEFAULT_CATEGORIES[category]
                template_key = template_in_category or "default"
                if template_key in category_templates:
                    return category_templates[template_key]
                raise ValueError(f"Template '{template_key}' not found in category '{category}'")
            raise ValueError(f"Category '{category}' not found")
        
        # Try custom templates
        template_name = template_name or "default"
        if template_name in self._custom:
            return self._custom[template_name]
        
        # Try legacy templates
        if template_name in self._legacy_templates:
            return self._legacy_templates[template_name]
        
        # Try default legacy prompts
        if template_name in DEFAULT_PROMPTS:
            return DEFAULT_PROMPTS[template_name]
        
        # Try default legacy prompts
        if template_name in LEGACY_DEFAULT_PROMPTS:
            return LEGACY_DEFAULT_PROMPTS[template_name]
        
        raise ValueError(f"Prompt template '{template_name}' not found")
    
    def list_prompts(self) -> List[str]:
        """List all available prompt template names (legacy and custom).
        
        Returns:
            List of template names.
        """
        all_templates = set()
        all_templates.update(self._custom.keys())
        all_templates.update(self._legacy_templates.keys())
        all_templates.update(DEFAULT_PROMPTS.keys())
        all_templates.update(LEGACY_DEFAULT_PROMPTS.keys())
        return sorted(list(all_templates))
    
    def list_categories(self) -> List[str]:
        """List all available template categories.
        
        Returns:
            List of category names.
        """
        categories = set()
        categories.update(self._categories.keys())
        categories.update(DEFAULT_CATEGORIES.keys())
        return sorted(list(categories))
    
    def list_templates_in_category(self, category: str) -> List[str]:
        """List templates in a specific category.
        
        Args:
            category: Category name.
        
        Returns:
            List of template names in the category.
        """
        templates = set()
        if category in self._categories:
            templates.update(self._categories[category].keys())
        if category in DEFAULT_CATEGORIES:
            templates.update(DEFAULT_CATEGORIES[category].keys())
        return sorted(list(templates))
    
    def save_prompt(
        self, 
        template_name: str, 
        prompt: str,
        category: Optional[str] = None
    ) -> None:
        """Save a prompt template to the YAML file.
        
        Args:
            template_name: Name of the template.
            prompt: Prompt template string.
            category: Optional category name. If provided, saves in categories section.
        """
        if category:
            if category not in self._categories:
                self._categories[category] = {}
            self._categories[category][template_name] = prompt
        else:
            self._custom[template_name] = prompt
        self._save_to_file()
    
    def _save_to_file(self) -> None:
        """Save templates to YAML file."""
        self.templates_file.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        
        if self._categories:
            data["categories"] = self._categories
        
        if self._custom:
            data["custom"] = self._custom
        
        # Preserve legacy templates for backward compatibility
        if self._legacy_templates:
            data["templates"] = self._legacy_templates
        
        with open(self.templates_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    def init_default_templates(self) -> Path:
        """Initialize templates.yaml file with default templates.
        
        Returns:
            Path to created templates file.
        """
        self._categories = DEFAULT_CATEGORIES.copy()
        self._custom = {}
        self._legacy_templates = LEGACY_DEFAULT_PROMPTS.copy()
        self._save_to_file()
        return self.templates_file

