"""Template management subcommand for txtguy."""

import sys
from pathlib import Path
from typing import Optional
import click
from txtguy.config import Config
from txtguy.domain.errors import ConfigError
from txtguy.prompts.manager import PromptManager


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]}
)
def template():
    """Manage template categories and custom templates.
    
    Templates control how your text files are summarized. txtguy comes with
    three built-in categories (short, long, blog) and supports custom templates.
    
    \b
    Commands:
      list      List all available templates and categories
      show      Display the content of a specific template
      create    Create a new template interactively
    
    \b
    Examples:
      # List all templates
      txtguy template list
      
      # List templates in a category
      txtguy template list --category short
      
      # Show a template
      txtguy template show default
      txtguy template show default --category short
      
      # Create a new template
      txtguy template create my_template
    """
    pass


@template.command("list")
@click.option(
    "--category",
    type=str,
    metavar="CATEGORY",
    help="List templates only in the specified category (short, long, or blog)."
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    metavar="PATH",
    help="Path to custom config file. Default: ~/.txtguy/config.yaml"
)
def list_templates(category, config):
    """List all available templates and categories.
    
    Shows template categories (short, long, blog) with their templates,
    as well as any custom templates you've created.
    
    \b
    Examples:
      # List all templates
      txtguy template list
      
      # List only short category templates
      txtguy template list --category short
    """
    try:
        cfg = Config(config_path=config) if config else Config()
        templates_file = cfg.get_templates_file()
        manager = PromptManager(templates_file)
        
        if category:
            # List templates in category
            templates = manager.list_templates_in_category(category)
            if templates:
                click.echo(f"\nTemplates in category '{category}':")
                for template_name in templates:
                    click.echo(f"  - {template_name}")
            else:
                click.echo(f"No templates found in category '{category}'", err=True)
        else:
            # List all categories and custom templates
            categories = manager.list_categories()
            custom_templates = manager.list_prompts()
            
            if categories:
                click.echo("\nTemplate Categories:")
                for cat in categories:
                    templates = manager.list_templates_in_category(cat)
                    click.echo(f"  {cat}:")
                    for template_name in templates:
                        click.echo(f"    - {template_name}")
            
            if custom_templates:
                click.echo("\nCustom Templates:")
                for template_name in custom_templates:
                    click.echo(f"  - {template_name}")
            
            if not categories and not custom_templates:
                click.echo("No templates found.")
    except ConfigError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@template.command("create")
@click.argument("name", type=str, metavar="NAME")
@click.option(
    "--category",
    type=str,
    metavar="CATEGORY",
    help="Category name (short, long, or blog). If not provided, creates a standalone custom template."
)
@click.option(
    "--editor",
    is_flag=True,
    help="Open template in your default editor ($EDITOR) for editing. Default: uses click.edit()"
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    metavar="PATH",
    help="Path to custom config file. Default: ~/.txtguy/config.yaml"
)
def create_template(name, category, editor, config):
    """Create a new template interactively.
    
    Opens an editor to create a new template. Use {content} as a placeholder
    for where the file content will be inserted.
    
    \b
    Arguments:
      NAME    Name for the new template
    
    \b
    Examples:
      # Create a custom template
      txtguy template create my_template
      
      # Create a template in the short category
      txtguy template create concise --category short
      
      # Use your default editor
      txtguy template create my_template --editor
    """
    try:
        cfg = Config(config_path=config) if config else Config()
        templates_file = cfg.get_templates_file()
        manager = PromptManager(templates_file)
        
        # Default template content
        default_content = (
            "Please process the following content:\n\n"
            "Content:\n{content}"
        )
        
        if editor:
            # Use system editor
            import tempfile
            import subprocess
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(default_content)
                temp_path = f.name
            
            editor_cmd = os.environ.get('EDITOR', 'nano')
            subprocess.run([editor_cmd, temp_path])
            
            with open(temp_path, 'r') as f:
                content = f.read()
            
            os.unlink(temp_path)
        else:
            content = click.edit(default_content) or default_content
        
        manager.save_prompt(name, content, category=category)
        
        if category:
            click.echo(f"Created template '{name}' in category '{category}'")
        else:
            click.echo(f"Created custom template '{name}'")
    except ConfigError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@template.command("show")
@click.argument("name", type=str, metavar="NAME")
@click.option(
    "--category",
    type=str,
    metavar="CATEGORY",
    help="Category name (short, long, or blog) if template is in a category."
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    metavar="PATH",
    help="Path to custom config file. Default: ~/.txtguy/config.yaml"
)
def show_template(name, category, config):
    """Show the content of a specific template.
    
    Displays the full template text, including placeholders like {content}.
    
    \b
    Arguments:
      NAME    Template name to display
    
    \b
    Examples:
      # Show a custom template
      txtguy template show my_template
      
      # Show a template from a category
      txtguy template show default --category short
    """
    try:
        cfg = Config(config_path=config) if config else Config()
        templates_file = cfg.get_templates_file()
        manager = PromptManager(templates_file)
        
        if category:
            template_content = manager.get_prompt(category=category, template_in_category=name)
        else:
            template_content = manager.get_prompt(name)
        
        click.echo(f"\nTemplate: {name}")
        if category:
            click.echo(f"Category: {category}")
        click.echo("=" * 60)
        click.echo(template_content)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ConfigError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
