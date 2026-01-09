"""Command-line interface for txtguy."""

import click
from txtguy import __version__


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]}
)
@click.version_option(version=__version__, prog_name="txtguy")
def cli():
    """txtguy - A versatile text processing tool with LLM integration.
    
    Process text files with AI-powered summarization, file renaming, and more.
    
    \b
    Commands:
      summarize    Summarize text files using LLM APIs with multiple format options
      rename       Suggest and rename files based on their content using AI
      template     Manage template categories (short/long/blog) and custom templates
      config       Manage configuration files and settings
    
    \b
    Examples:
      # Summarize a file with default format
      txtguy summarize document.txt
      
      # Summarize with short format
      txtguy summarize document.txt --format short
      
      # Rename files with AI suggestions
      txtguy rename *.srt
      
      # List available templates
      txtguy template list
      
      # Show current configuration
      txtguy config show
    
    \b
    For more information, use: txtguy <command> --help
    """
    pass


# Import subcommands to register them
from txtguy.cli.summarize import summarize
from txtguy.cli.rename import rename
from txtguy.cli.template import template
from txtguy.cli.config import config

# Register subcommands
cli.add_command(summarize)
cli.add_command(rename)
cli.add_command(template)
cli.add_command(config)


# Main entry point
def main():
    """Main entry point for txtguy command."""
    cli()


if __name__ == "__main__":
    main()
