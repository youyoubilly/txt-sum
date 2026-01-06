"""Command-line interface for SRT Summarizor."""

import sys
from pathlib import Path
from typing import Optional
import click
from srt_summarizor import __version__
from srt_summarizor.config import Config
from srt_summarizor.summarizer import Summarizer
from srt_summarizor.parser import SubtitleParser


def _discover_subtitle_files(directory: Path) -> list[Path]:
    """Discover all subtitle files in a directory (top-level only).
    
    Args:
        directory: Path to directory to scan.
    
    Returns:
        List of subtitle file paths found in the directory.
    """
    supported_extensions = {".srt", ".txt", ".vtt", ".ass", ".ssa"}
    subtitle_files = []
    
    try:
        for item in directory.iterdir():
            if item.is_file() and item.suffix.lower() in supported_extensions:
                subtitle_files.append(item)
    except PermissionError:
        raise ValueError(f"Permission denied: Cannot read directory {directory}")
    except Exception as e:
        raise ValueError(f"Error scanning directory {directory}: {e}")
    
    return sorted(subtitle_files)


def _get_output_path(input_file: Path, output_dir: Optional[Path] = None) -> Path:
    """Get expected output path for an input file.
    
    Args:
        input_file: Path to input subtitle file.
        output_dir: Optional output directory. If None, uses same directory as input.
    
    Returns:
        Expected output file path.
    """
    if output_dir:
        return output_dir / f"{input_file.stem}.md"
    else:
        return input_file.with_suffix(".md")


def _read_context(context_input: Optional[str]) -> Optional[str]:
    """Read context from text or file.
    
    Args:
        context_input: Either direct text or a file path.
    
    Returns:
        Context string, or None if context_input is None.
    
    Raises:
        FileNotFoundError: If file path doesn't exist.
        ValueError: If file reading fails.
    """
    if not context_input:
        return None
    
    # Check if it's a file path
    context_path = Path(context_input)
    if context_path.exists() and context_path.is_file():
        try:
            # Use the same encoding detection as subtitle parser
            encoding = SubtitleParser.detect_encoding(context_path)
            with open(context_path, "r", encoding=encoding) as f:
                return f.read().strip()
        except Exception as e:
            raise ValueError(f"Failed to read context file {context_path}: {e}") from e
    
    # Treat as direct text
    return context_input.strip()


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
@click.version_option(version=__version__)
def main(files, output, prompt_template, provider, config, init_config, verbose, language, context, force):
    """SRT Summarizor - Summarize subtitle files using LLM APIs.
    
    FILES: One or more subtitle files or directories to process (SRT, TXT, VTT, ASS/SSA)
    """
    # Initialize config if requested
    if init_config:
        config_path = Config.init_config()
        click.echo(f"Configuration file initialized at: {config_path}")
        click.echo("Please edit it to configure your LLM provider and settings.")
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
    
    # Expand directories to files and collect all subtitle files
    input_files = []
    supported_extensions = {".srt", ".txt", ".vtt", ".ass", ".ssa"}
    
    for path in input_paths:
        if path.is_dir():
            # Discover subtitle files in directory
            try:
                dir_files = _discover_subtitle_files(path)
                input_files.extend(dir_files)
                if verbose:
                    click.echo(f"Found {len(dir_files)} subtitle file(s) in {path}")
            except ValueError as e:
                click.echo(f"Error: {e}", err=True)
                sys.exit(1)
        elif path.is_file():
            # Check if it's a supported subtitle file
            if path.suffix.lower() in supported_extensions:
                input_files.append(path)
            else:
                click.echo(f"Warning: Skipping unsupported file format: {path}", err=True)
        else:
            click.echo(f"Error: Path does not exist: {path}", err=True)
            sys.exit(1)
    
    if not input_files:
        click.echo("Error: No subtitle files found to process.", err=True)
        sys.exit(1)
    
    # Read context if provided
    extra_context = None
    if context:
        try:
            extra_context = _read_context(context)
        except (FileNotFoundError, ValueError) as e:
            click.echo(f"Error reading context: {e}", err=True)
            sys.exit(1)
    
    # Filter files based on output existence and force flag
    files_to_process = []
    skipped_files = []
    
    for input_file in input_files:
        output_path = _get_output_path(input_file, output_dir=output if output and output.is_dir() else None)
        
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
    
    # Process files
    try:
        if len(files_to_process) == 1:
            # Single file processing
            input_file = files_to_process[0]
            output_file = output
            
            if verbose:
                click.echo(f"Processing: {input_file}")
                if len(skipped_files) > 0:
                    click.echo(f"Skipped {len(skipped_files)} file(s) (use --force to overwrite)")
                if prompt_template:
                    click.echo(f"Using prompt template: {prompt_template}")
                if provider:
                    click.echo(f"Using provider: {provider}")
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
                extra_context=extra_context
            )
            
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
                click.echo(f"\nProcessing {len(files_to_process)} file(s)...")
                if len(skipped_files) > 0:
                    click.echo(f"Skipped {len(skipped_files)} file(s) (use --force to overwrite)")
                if prompt_template:
                    click.echo(f"Using prompt template: {prompt_template}")
                if provider:
                    click.echo(f"Using provider: {provider}")
                click.echo(f"Summary language: {language}")
                if extra_context:
                    click.echo(f"Using additional context: {len(extra_context)} characters")
                if force:
                    click.echo("Force mode: Overwriting existing output files")
            
            results = summarizer.summarize_files(
                files_to_process,
                output_dir=output_dir,
                prompt_template=prompt_template,
                provider=provider,
                language=language,
                extra_context=extra_context
            )
            
            if results:
                click.echo(f"\nSuccessfully processed {len(results)} file(s):")
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

