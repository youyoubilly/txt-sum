"""Summarize subcommand for txtguy."""

import sys
from pathlib import Path
from typing import Optional
import click
from txtguy.config import Config
from txtguy.summarizer import Summarizer
from txtguy.domain.errors import (
    TxtSumError,
    ConfigError,
    ParseError,
    ProviderError,
    ContentTooLongError,
)
from txtguy.utils.file_utils import (
    discover_text_files,
    get_output_path,
    check_file_size,
    is_binary_file,
)
from txtguy.utils.cli_utils import read_context
from txtguy.cli.base import BaseSubcommand


@click.command()
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True, path_type=Path), metavar="FILES...")
@click.option(
    "-o", "--output",
    type=click.Path(path_type=Path),
    metavar="PATH",
    help="Output file path (single file) or directory (multiple files). Default: same directory as input with .md extension."
)
@click.option(
    "--format",
    type=click.Choice(["short", "long", "blog"], case_sensitive=False),
    metavar="FORMAT",
    help="Summary format category: 'short' (2-3 sentences), 'long' (detailed with sections), or 'blog' (article-style)."
)
@click.option(
    "-t", "--template",
    type=str,
    metavar="NAME",
    help="Use a specific template by name. Can be combined with --category. Overrides --format."
)
@click.option(
    "--category",
    type=click.Choice(["short", "long", "blog"], case_sensitive=False),
    metavar="CATEGORY",
    help="Template category to use with --template. Required when using templates from categories."
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
    "-l", "--language",
    type=str,
    default="en",
    metavar="CODE",
    help="Language code for the summary output. Examples: en, zh, es, fr, de, ja, ko. Default: en"
)
@click.option(
    "-c", "--context",
    type=str,
    metavar="TEXT_OR_FILE",
    help="Additional context for better summarization. Can be direct text or a file path containing context."
)
@click.option(
    "-f", "--force",
    is_flag=True,
    help="Force processing and overwrite existing output files."
)
@click.option(
    "--force-text",
    is_flag=True,
    help="Force processing of unknown file types as text (even if format is unrecognized)."
)
@click.option(
    "--full-context",
    is_flag=True,
    help="Preserve timestamps and formatting in subtitle files (default: strips formatting)."
)
def summarize(files, output, format, template, category, provider, config, verbose, language, context, force, force_text, full_context):
    """Summarize text files using LLM APIs.
    
    Process one or more text files (SRT, TXT, VTT, ASS/SSA, or any text file)
    and generate summaries in various formats.
    
    \b
    Arguments:
      FILES...    One or more text files or directories to process
    
    \b
    Format Options:
      --format short    Brief summary (2-3 sentences)
      --format long     Detailed summary with structured sections
      --format blog     Blog-style article with engaging introduction
    
    \b
    Examples:
      # Basic summarization
      txtguy summarize document.txt
      
      # Short format summary
      txtguy summarize episode.srt --format short
      
      # Blog-style article
      txtguy summarize meeting.txt --format blog
      
      # Custom template from category
      txtguy summarize file.txt --template default --category short
      
      # With additional context
      txtguy summarize call.srt -c "This is a sales call"
      
      # Batch process directory
      txtguy summarize /path/to/files/ -o ~/summaries/
      
      # Multiple languages
      txtguy summarize document.txt -l zh
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
    
    # Determine template to use
    prompt_template = None
    if template:
        # If template contains colon, it's already in category:template format
        if ":" in template:
            prompt_template = template
        elif category:
            # Use category:template format
            prompt_template = f"{category}:{template}"
        else:
            prompt_template = template
    elif format:
        # Use default template from the category
        prompt_template = f"{format}:default"
    
    # Expand directories to files and collect all text files
    input_files = []
    supported_extensions = {".srt", ".txt", ".vtt", ".ass", ".ssa"}
    
    for path in files:
        if path.is_dir():
            # Discover text files in directory
            try:
                dir_files = discover_text_files(path, force_text=force_text, supported_extensions=supported_extensions)
                input_files.extend(dir_files)
                if verbose:
                    click.echo(f"Found {len(dir_files)} text file(s) in {path}")
            except ValueError as e:
                click.echo(f"Error: {e}", err=True)
                sys.exit(1)
        elif path.is_file():
            # Check if it's a known format or text-based
            suffix = path.suffix.lower()
            if suffix in supported_extensions:
                input_files.append(path)
            elif force_text or (not is_binary_file(path)):
                input_files.append(path)
            else:
                click.echo(f"Warning: Skipping binary file: {path}. Use --force-text to process anyway.", err=True)
        else:
            click.echo(f"Error: Path does not exist: {path}", err=True)
            sys.exit(1)
    
    if not input_files:
        click.echo("Error: No text files found to process.", err=True)
        sys.exit(1)
    
    # Warn about large files
    large_files = []
    for input_file in input_files:
        if check_file_size(input_file):
            large_files.append(input_file)
    
    if large_files and verbose:
        click.echo(f"Warning: {len(large_files)} file(s) are large (>10MB). Processing may take longer.")
    
    # Read context if provided
    extra_context = None
    if context:
        try:
            extra_context = read_context(context)
        except (FileNotFoundError, ValueError) as e:
            click.echo(f"Error reading context: {e}", err=True)
            sys.exit(1)
    
    # Filter files based on output existence and force flag
    files_to_process = []
    skipped_files = []
    
    for input_file in input_files:
        output_path = get_output_path(input_file, output_dir=output if output and output.is_dir() else None)
        
        if output_path.exists() and not force:
            skipped_files.append((input_file, output_path))
            if verbose:
                click.echo(f"Skipping {input_file.name} (output already exists: {output_path})")
        else:
            files_to_process.append(input_file)
    
    if not files_to_process:
        if skipped_files:
            click.echo(f"All {len(skipped_files)} file(s) already have summaries. Use --force to overwrite.")
        else:
            click.echo("No files to process.", err=True)
        sys.exit(0)
    
    if skipped_files and verbose:
        click.echo(f"\nSkipped {len(skipped_files)} file(s) (output already exists)")
    
    # Initialize summarizer
    try:
        summarizer = Summarizer(cfg)
    except ConfigError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)
    except ProviderError as e:
        click.echo(f"Provider error: {e}", err=True)
        click.echo("Please check your LLM provider configuration in ~/.txtguy/config.yaml", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error initializing summarizer: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    # Display provider and template information
    current_provider = provider or cfg.get("llm_provider", "lm_studio")
    templates_file_path = cfg.get_templates_file()
    current_template = prompt_template or cfg.get("default_prompt_template", "default")
    
    click.echo(f"Using LLM provider: {current_provider}")
    click.echo(f"Using templates from: {templates_file_path}")
    click.echo(f"Using template: {current_template}")
    click.echo()
    
    # Process files
    try:
        if len(files_to_process) == 1:
            # Single file processing
            input_file = files_to_process[0]
            output_file = output
            
            # Display file being processed
            click.echo(f"Processing: {input_file.name}")
            
            if verbose:
                if len(skipped_files) > 0:
                    click.echo(f"Skipped {len(skipped_files)} file(s) (use --force to overwrite)")
                click.echo(f"Summary language: {language}")
                if extra_context:
                    click.echo(f"Using additional context: {len(extra_context)} characters")
                if force:
                    click.echo("Force mode: Overwriting existing output file")
            
            try:
                result = summarizer.summarize_file(
                    input_file,
                    output_file=output_file,
                    prompt_template=prompt_template,
                    provider=provider,
                    language=language,
                    extra_context=extra_context,
                    full_context=full_context,
                    force_text=force_text
                )
            except ContentTooLongError as e:
                click.echo(f"Error: {e}", err=True)
                sys.exit(1)
            except ParseError as e:
                click.echo(f"Parse error: {e}", err=True)
                sys.exit(1)
            except ProviderError as e:
                click.echo(f"Provider error: {e}", err=True)
                sys.exit(1)
            
            if result is None:
                click.echo("File was skipped.", err=True)
                sys.exit(0)
            
            click.echo(f"Summary saved to: {result}")
            
            if len(skipped_files) > 0:
                click.echo(f"\nSkipped {len(skipped_files)} file(s) (output already exists)")
        
        else:
            # Batch processing
            output_dir = output if output and output.is_dir() else None
            if output and not output.is_dir():
                click.echo(f"Warning: Output path is not a directory. Using default output location.", err=True)
                output_dir = None
            
            if verbose:
                if len(skipped_files) > 0:
                    click.echo(f"Skipped {len(skipped_files)} file(s) (use --force to overwrite)")
                click.echo(f"Summary language: {language}")
                if extra_context:
                    click.echo(f"Using additional context: {len(extra_context)} characters")
                if force:
                    click.echo("Force mode: Overwriting existing output files")
                click.echo()
            
            # Process files with progress display
            results = []
            total_files = len(files_to_process)
            
            for idx, input_file in enumerate(files_to_process, 1):
                click.echo(f"Processing [{idx}/{total_files}]: {input_file.name}")
                
                try:
                    # Determine output filename
                    output_file = None
                    if output_dir:
                        output_file = output_dir / f"{input_file.stem}.md"
                    
                    result = summarizer.summarize_file(
                        input_file,
                        output_file=output_file,
                        prompt_template=prompt_template,
                        provider=provider,
                        language=language,
                        extra_context=extra_context,
                        full_context=full_context,
                        force_text=force_text
                    )
                    
                    if result is not None:
                        results.append(result)
                except ContentTooLongError as e:
                    click.echo(f"  Skipped: Content too long ({e.content_length} > {e.max_length} characters)", err=True)
                    continue
                except ParseError as e:
                    click.echo(f"  Parse error: {e}", err=True)
                    if verbose:
                        import traceback
                        traceback.print_exc()
                    continue
                except ProviderError as e:
                    click.echo(f"  Provider error: {e}", err=True)
                    if verbose:
                        import traceback
                        traceback.print_exc()
                    continue
                except TxtSumError as e:
                    click.echo(f"  Error: {e}", err=True)
                    if verbose:
                        import traceback
                        traceback.print_exc()
                    continue
                except Exception as e:
                    # Continue with other files even if one fails
                    click.echo(f"  Unexpected error: {e}", err=True)
                    if verbose:
                        import traceback
                        traceback.print_exc()
                    continue
            
            click.echo()  # Blank line before summary
            
            if results:
                click.echo(f"Successfully processed {len(results)} file(s):")
                for result in results:
                    click.echo(f"  - {result}")
                if len(skipped_files) > 0:
                    click.echo(f"\nSkipped {len(skipped_files)} file(s) (output already exists)")
            else:
                click.echo("No files were successfully processed.", err=True)
                sys.exit(1)
    
    except ContentTooLongError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ParseError as e:
        click.echo(f"Parse error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except ProviderError as e:
        click.echo(f"Provider error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except ConfigError as e:
        click.echo(f"Configuration error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except TxtSumError as e:
        click.echo(f"Error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except FileNotFoundError as e:
        click.echo(f"File not found: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Value error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
