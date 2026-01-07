"""Command-line interface for txt-sum."""

import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import click
from txt_sum import __version__
from txt_sum.config import Config
from txt_sum.summarizer import Summarizer
from txt_sum.utils.file_utils import (
    discover_text_files,
    get_output_path,
    check_file_size,
    is_binary_file,
)
from txt_sum.utils.cli_utils import (
    read_context,
)


@click.command()
@click.argument("files", nargs=-1, required=False, type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o", "--output",
    type=click.Path(path_type=Path),
    help="Output file path (for single file) or directory (for multiple files)"
)
@click.option(
    "-p", "--prompt-template",
    type=str,
    help="Prompt template name to use (default: from config)"
)
@click.option(
    "--provider",
    type=click.Choice(["lm_studio", "openai", "qwen"], case_sensitive=False),
    help="LLM provider to use (overrides config)"
)
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to custom config file"
)
@click.option(
    "--init-config",
    is_flag=True,
    help="Initialize config file in default location and exit"
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Verbose output"
)
@click.option(
    "-l", "--language",
    type=str,
    default="en",
    help="Language code for the summary (default: en). Examples: en, zh, es, fr, de, ja, ko"
)
@click.option(
    "-c", "--context",
    type=str,
    help="Additional context to help with summarization. Can be direct text or a file path."
)
@click.option(
    "-f", "--force",
    is_flag=True,
    help="Force processing even if output file already exists (overwrite existing files)"
)
@click.option(
    "--force-text",
    is_flag=True,
    help="Force processing of unknown file types (attempt to process as text even if format is unknown)"
)
@click.option(
    "--full-context",
    is_flag=True,
    help="Process subtitle files with full context (preserve timestamps and formatting)"
)
@click.version_option(version=__version__)
def main(files, output, prompt_template, provider, config, init_config, verbose, language, context, force, force_text, full_context):
    """txt-sum - Summarize text files using LLM APIs.
    
    FILES: One or more text files or directories to process
    """
    # Initialize config if requested
    if init_config:
        config_path = Config.init_config()
        prompts_path = Config.PROMPTS_FILE
        click.echo(f"Configuration file initialized at: {config_path}")
        click.echo(f"Prompts file initialized at: {prompts_path}")
        click.echo("Please edit them to configure your LLM provider, settings, and prompt templates.")
        return
    
    # Load configuration
    try:
        cfg = Config(config_path=config) if config else Config()
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        click.echo("Run with --init-config to create a default config file.", err=True)
        sys.exit(1)
    
    # Validate and expand input paths (files and directories)
    input_paths = list(files) if files else []
    if not input_paths and not init_config:
        click.echo("Error: No input files or directories specified.", err=True)
        click.echo("Use --help for usage information or --init-config to initialize config.", err=True)
        sys.exit(1)
    
    # Expand directories to files and collect all text files
    input_files = []
    supported_extensions = {".srt", ".txt", ".vtt", ".ass", ".ssa"}
    
    for path in input_paths:
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
    except Exception as e:
        click.echo(f"Error initializing summarizer: {e}", err=True)
        sys.exit(1)
    
    # Display provider and prompt template information
    current_provider = provider or cfg.get("llm_provider", "lm_studio")
    prompts_file_path = cfg.get_prompts_file()
    current_prompt_template = prompt_template or cfg.get("default_prompt_template", "default")
    
    click.echo(f"Using LLM provider: {current_provider}")
    click.echo(f"Using prompt templates from: {prompts_file_path}")
    click.echo(f"Using prompt template: {current_prompt_template}")
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
            
            if result is None:
                # Check if it was due to length
                from txt_sum.parser import SubtitleParser
                try:
                    content = SubtitleParser.extract_text(input_file, full_context=full_context, force_text=force_text)
                    if len(content) > summarizer.max_text_length:
                        click.echo(
                            f"Warning: File '{input_file.name}' exceeds maximum text length "
                            f"({len(content)} characters > {summarizer.max_text_length} limit). Skipping...",
                            err=True
                        )
                except Exception:
                    pass
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
                    else:
                        # File was skipped (likely due to length)
                        from txt_sum.parser import SubtitleParser
                        try:
                            content = SubtitleParser.extract_text(input_file, full_context=full_context, force_text=force_text)
                            if len(content) > summarizer.max_text_length:
                                click.echo(
                                    f"  Warning: Exceeds maximum text length "
                                    f"({len(content)} > {summarizer.max_text_length} characters). Skipped.",
                                    err=True
                                )
                        except Exception:
                            pass
                except Exception as e:
                    # Continue with other files even if one fails
                    click.echo(f"  Error: {e}", err=True)
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
    
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
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


if __name__ == "__main__":
    main()

