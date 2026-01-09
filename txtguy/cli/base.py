"""Base classes for subcommands."""

import click
from typing import Optional
from pathlib import Path
from txtguy.config import Config
from txtguy.domain.errors import TxtSumError


class BaseSubcommand:
    """Base class for subcommands with common functionality."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize subcommand with config.
        
        Args:
            config_path: Optional custom config file path.
        """
        try:
            self.config = Config(config_path=config_path) if config_path else Config()
        except Exception as e:
            raise click.ClickException(f"Configuration error: {e}")
    
    def handle_error(self, error: Exception, verbose: bool = False) -> None:
        """Handle errors consistently across subcommands.
        
        Args:
            error: Exception to handle.
            verbose: Whether to show detailed error information.
        """
        if isinstance(error, TxtSumError):
            click.echo(f"Error: {error}", err=True)
        else:
            click.echo(f"Unexpected error: {error}", err=True)
            if verbose:
                import traceback
                traceback.print_exc()
