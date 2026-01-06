"""Command-line interface for SRT Summarizor."""

import sys
from pathlib import Path
import click
from srt_summarizor import __version__
from srt_summarizor.config import Config
from srt_summarizor.summarizer import Summarizer


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
@click.version_option(version=__version__)
def main(files, output, prompt_template, provider, config, init_config, verbose, language):
    """SRT Summarizor - Summarize subtitle files using LLM APIs.
    
    FILES: One or more subtitle files to process (SRT, TXT, VTT, ASS/SSA)
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
    
    # Validate input files (only if not initializing config)
    input_files = list(files) if files else []
    if not input_files and not init_config:
        click.echo("Error: No input files specified.", err=True)
        click.echo("Use --help for usage information or --init-config to initialize config.", err=True)
        sys.exit(1)
    
    # Check file extensions
    supported_extensions = {".srt", ".txt", ".vtt", ".ass", ".ssa"}
    invalid_files = [f for f in input_files if f.suffix.lower() not in supported_extensions]
    if invalid_files:
        click.echo(f"Error: Unsupported file format(s): {', '.join(str(f) for f in invalid_files)}", err=True)
        click.echo(f"Supported formats: {', '.join(supported_extensions)}", err=True)
        sys.exit(1)
    
    # Initialize summarizer
    try:
        summarizer = Summarizer(cfg)
    except Exception as e:
        click.echo(f"Error initializing summarizer: {e}", err=True)
        sys.exit(1)
    
    # Process files
    try:
        if len(input_files) == 1:
            # Single file processing
            input_file = input_files[0]
            output_file = output
            
            if verbose:
                click.echo(f"Processing: {input_file}")
                if prompt_template:
                    click.echo(f"Using prompt template: {prompt_template}")
                if provider:
                    click.echo(f"Using provider: {provider}")
                click.echo(f"Summary language: {language}")
            
            result = summarizer.summarize_file(
                input_file,
                output_file=output_file,
                prompt_template=prompt_template,
                provider=provider,
                language=language
            )
            
            click.echo(f"Summary saved to: {result}")
        
        else:
            # Batch processing
            output_dir = output if output and output.is_dir() else None
            if output and not output.is_dir():
                click.echo(f"Warning: Output path is not a directory. Using default output location.", err=True)
                output_dir = None
            
            if verbose:
                click.echo(f"Processing {len(input_files)} files...")
                if prompt_template:
                    click.echo(f"Using prompt template: {prompt_template}")
                if provider:
                    click.echo(f"Using provider: {provider}")
                click.echo(f"Summary language: {language}")
            
            results = summarizer.summarize_files(
                input_files,
                output_dir=output_dir,
                prompt_template=prompt_template,
                provider=provider,
                language=language
            )
            
            if results:
                click.echo(f"\nSuccessfully processed {len(results)} file(s):")
                for result in results:
                    click.echo(f"  - {result}")
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

