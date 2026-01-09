"""Rename subcommand for txtguy."""

import sys
from pathlib import Path
from typing import Optional
import click
from txtguy.config import Config
from txtguy.domain.errors import ConfigError, ProviderError
from txtguy.llm.registry import ProviderRegistry
from txtguy.app.filename_suggest import suggest_filenames, suggest_filenames_from_content
from txtguy.utils.cli_utils import interactive_filename_selection, rename_files
from txtguy.utils.text_utils import extract_summary_from_markdown
from txtguy.parser import SubtitleParser
from txtguy.cli.base import BaseSubcommand


@click.command()
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True, path_type=Path), metavar="FILES...")
@click.option(
    "--with-summary",
    type=click.Path(exists=True, path_type=Path),
    metavar="PATH",
    help="Use existing summary file (.md) for better filename suggestions. If not provided, analyzes file content directly."
)
@click.option(
    "--provider",
    type=click.Choice(["lm_studio", "openai", "qwen"], case_sensitive=False),
    metavar="PROVIDER",
    help="LLM provider to use (overrides config): 'lm_studio', 'openai', or 'qwen'."
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    metavar="PATH",
    help="Path to custom config file. Default: ~/.txtguy/config.yaml"
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose output with detailed processing information."
)
@click.option(
    "--force-text",
    is_flag=True,
    help="Force processing of unknown file types as text (even if format is unrecognized)."
)
def rename(files, with_summary, provider, config, verbose, force_text):
    """Suggest and rename files based on their content using AI.
    
    Analyzes file content (or existing summary) to suggest better, more descriptive
    filenames. Provides interactive selection from multiple suggestions.
    
    \b
    Arguments:
      FILES...    One or more text files to rename
    
    \b
    Examples:
      # Rename a single file
      txtguy rename document.srt
      
      # Rename with existing summary for better suggestions
      txtguy rename document.srt --with-summary document.md
      
      # Batch rename multiple files
      txtguy rename *.srt
      
      # Rename files in a directory
      txtguy rename /path/to/files/*.txt
    """
    # Load configuration
    try:
        cfg = Config(config_path=config) if config else Config()
    except ConfigError as e:
        click.echo(f"Configuration error: {e}", err=True)
        click.echo("Run 'txtguy config init' to create a default config file.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    # Get LLM provider
    try:
        provider_name = provider or cfg.get("llm_provider", "lm_studio")
        settings = cfg.get_llm_settings(provider_name)
        llm_provider = ProviderRegistry.get_provider(provider_name, settings)
    except ProviderError as e:
        click.echo(f"Provider error: {e}", err=True)
        click.echo("Please check your LLM provider configuration in ~/.txtguy/config.yaml", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error initializing LLM provider: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    # Process each file
    for input_file in files:
        input_path = Path(input_file)
        
        if not input_path.is_file():
            click.echo(f"Warning: Skipping {input_path} (not a file)", err=True)
            continue
        
        click.echo(f"\nProcessing: {input_path.name}")
        
        # Determine output file (look for .md file with same stem)
        output_file = None
        if with_summary:
            output_file = Path(with_summary)
        else:
            # Look for corresponding .md file
            potential_output = input_path.with_suffix(".md")
            if potential_output.exists():
                output_file = potential_output
        
        # Get suggestions
        suggestions = None
        
        if output_file and output_file.exists():
            # Use summary file for suggestions
            try:
                summary_content = extract_summary_from_markdown(output_file)
                if summary_content:
                    suggestions = suggest_filenames(input_path, output_file, summary_content, llm_provider)
                    if verbose:
                        click.echo(f"Using summary from: {output_file.name}")
            except Exception as e:
                if verbose:
                    click.echo(f"Warning: Could not read summary file: {e}", err=True)
        
        if not suggestions or not suggestions.get("original") or not suggestions.get("output"):
            # Fall back to content-based suggestions
            try:
                content = SubtitleParser.extract_text(input_path, force_text=force_text)
                if content:
                    # Use first 2000 chars for suggestions
                    content_excerpt = content[:2000] + ("..." if len(content) > 2000 else "")
                    suggestions = suggest_filenames_from_content(input_path, content_excerpt, llm_provider)
                    if verbose:
                        click.echo("Using file content for suggestions")
            except Exception as e:
                click.echo(f"Error reading file content: {e}", err=True)
                continue
        
        if not suggestions or not suggestions.get("original") or not suggestions.get("output"):
            click.echo(f"Warning: Could not generate suggestions for {input_path.name}", err=True)
            continue
        
        # Interactive selection
        selected = interactive_filename_selection(input_path, output_file, suggestions)
        
        if selected:
            # Rename files
            try:
                result = rename_files(input_path, output_file or input_path.with_suffix(".md"), selected)
                if verbose:
                    click.echo(f"Successfully renamed files for {input_path.name}")
            except Exception as e:
                click.echo(f"Error renaming files: {e}", err=True)
        else:
            if verbose:
                click.echo(f"Skipped renaming for {input_path.name}")
