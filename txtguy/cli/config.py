"""Config management subcommand for txtguy."""

import sys
from pathlib import Path
from typing import Optional
import click
from txtguy.config import Config
from txtguy.domain.errors import ConfigError


# Create a group for config subcommands
@click.group(
    context_settings={"help_option_names": ["-h", "--help"]}
)
def config():
    """Manage configuration files and settings.
    
    Configuration files are stored in ~/.txtguy/ by default. The config.yaml
    file contains LLM provider settings, and templates.yaml contains your
    template categories and custom templates.
    
    \b
    Commands:
      init    Initialize configuration files with defaults
      show    Display current configuration settings
    
    \b
    Examples:
      # Initialize config files
      txtguy config init
      
      # Show current configuration
      txtguy config show
    """
    pass


@config.command("init")
@click.option(
    "--config-path",
    type=click.Path(path_type=Path),
    metavar="PATH",
    help="Custom path for config file. Default: ~/.txtguy/config.yaml"
)
def init(config_path):
    """Initialize configuration files with default settings.
    
    Creates config.yaml and templates.yaml in ~/.txtguy/ (or custom path)
    with default templates and LLM provider configurations.
    
    \b
    Examples:
      # Initialize with default location
      txtguy config init
      
      # Initialize with custom path
      txtguy config init --config-path /custom/path/config.yaml
    """
    try:
        config_file = Config.init_config(config_path=config_path)
        templates_file = Config.TEMPLATES_FILE
        
        click.echo(f"Configuration file initialized at: {config_file}")
        click.echo(f"Templates file initialized at: {templates_file}")
        click.echo("\nPlease edit them to configure your LLM provider, settings, and templates.")
    except Exception as e:
        click.echo(f"Error initializing config: {e}", err=True)
        sys.exit(1)


@config.command("show")
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    metavar="PATH",
    help="Path to custom config file. Default: ~/.txtguy/config.yaml"
)
def show(config):
    """Display current configuration settings.
    
    Shows the active configuration including LLM provider, template settings,
    file paths, and other options.
    
    \b
    Examples:
      # Show default config
      txtguy config show
      
      # Show custom config
      txtguy config show --config /custom/path/config.yaml
    """
    try:
        cfg = Config(config_path=config) if config else Config()
        
        click.echo("Current Configuration:")
        click.echo("=" * 60)
        click.echo(f"Config file: {cfg.config_path}")
        click.echo(f"Templates file: {cfg.get_templates_file()}")
        click.echo(f"LLM Provider: {cfg.get('llm_provider', 'lm_studio')}")
        click.echo(f"Default template: {cfg.get('default_prompt_template', 'default')}")
        click.echo(f"Max text length: {cfg.get('max_text_length', 100000)}")
        click.echo(f"Default output path: {cfg.get('default_output_path', '~/Documents/summaries')}")
    except ConfigError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
