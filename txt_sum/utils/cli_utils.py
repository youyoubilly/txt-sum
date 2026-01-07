"""CLI helper functions."""

from pathlib import Path
from typing import Optional, Dict, List
import click
from txt_sum.utils.file_utils import detect_encoding


def read_context(context_input: Optional[str]) -> Optional[str]:
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
            # Use the same encoding detection as file utils
            encoding = detect_encoding(context_path)
            with open(context_path, "r", encoding=encoding) as f:
                return f.read().strip()
        except Exception as e:
            raise ValueError(f"Failed to read context file {context_path}: {e}") from e
    
    # Treat as direct text
    return context_input.strip()


def interactive_filename_selection(
    input_file: Path,
    output_file: Path,
    suggestions: Dict[str, List[str]]
) -> Optional[Dict[str, str]]:
    """Interactively ask user to select filenames from suggestions.
    
    Args:
        input_file: Original input file path.
        output_file: Original output file path.
        suggestions: Dictionary with "original" and "output" keys, each containing list of suggestions.
    
    Returns:
        Dictionary with "original" and "output" keys containing selected filenames, or None if user cancels.
    """
    original_suggestions = suggestions.get("original", [])
    output_suggestions = suggestions.get("output", [])
    
    if not original_suggestions or not output_suggestions:
        click.echo("Warning: Could not generate filename suggestions. Keeping original filenames.", err=True)
        return None
    
    click.echo("\n" + "="*60)
    click.echo("Filename Suggestions")
    click.echo("="*60)
    
    # Display original file suggestions
    click.echo(f"\nOriginal file: {input_file.name}")
    click.echo("Suggested filenames:")
    click.echo("  0. Keep original filename")
    for i, suggestion in enumerate(original_suggestions[:5], 1):
        click.echo(f"  {i}. {suggestion}")
    
    while True:
        try:
            choice_original = click.prompt(
                "\nSelect filename for original file (0-5)",
                type=click.IntRange(0, 5),
                default=0
            )
            break
        except click.Abort:
            return None
        except Exception:
            click.echo("Invalid input. Please enter a number between 0 and 5.", err=True)
    
    # Display output file suggestions
    click.echo(f"\nOutput file: {output_file.name}")
    click.echo("Suggested filenames:")
    click.echo("  0. Keep original filename")
    for i, suggestion in enumerate(output_suggestions[:5], 1):
        click.echo(f"  {i}. {suggestion}")
    
    while True:
        try:
            choice_output = click.prompt(
                "\nSelect filename for output file (0-5)",
                type=click.IntRange(0, 5),
                default=0
            )
            break
        except click.Abort:
            return None
        except Exception:
            click.echo("Invalid input. Please enter a number between 0 and 5.", err=True)
    
    # Determine selected filenames
    selected_original = input_file.name if choice_original == 0 else original_suggestions[choice_original - 1]
    selected_output = output_file.name if choice_output == 0 else output_suggestions[choice_output - 1]
    
    # Show confirmation
    click.echo("\nSelected filenames:")
    click.echo(f"  Original: {selected_original}")
    click.echo(f"  Output: {selected_output}")
    
    try:
        if not click.confirm("\nProceed with renaming?", default=True):
            return None
    except click.Abort:
        return None
    
    return {
        "original": selected_original,
        "output": selected_output
    }


def rename_files(
    input_file: Path,
    output_file: Path,
    new_names: Dict[str, str]
) -> Dict[str, Path]:
    """Rename files based on user selection.
    
    Args:
        input_file: Original input file path.
        output_file: Original output file path.
        new_names: Dictionary with "original" and "output" keys containing new filenames.
    
    Returns:
        Dictionary with "original" and "output" keys containing new file paths.
    
    Raises:
        ValueError: If renaming fails.
    """
    result = {"original": input_file, "output": output_file}
    
    # Rename original file if needed
    if new_names["original"] != input_file.name:
        new_input_path = input_file.parent / new_names["original"]
        
        # Check for conflicts
        if new_input_path.exists() and new_input_path != input_file:
            click.echo(f"Warning: {new_input_path} already exists. Skipping rename of original file.", err=True)
        else:
            try:
                input_file.rename(new_input_path)
                result["original"] = new_input_path
                click.echo(f"Renamed original file to: {new_input_path.name}")
            except Exception as e:
                click.echo(f"Error renaming original file: {e}", err=True)
    
    # Rename output file if needed
    if new_names["output"] != output_file.name:
        new_output_path = output_file.parent / new_names["output"]
        
        # Check for conflicts
        if new_output_path.exists() and new_output_path != output_file:
            click.echo(f"Warning: {new_output_path} already exists. Skipping rename of output file.", err=True)
        else:
            try:
                output_file.rename(new_output_path)
                result["output"] = new_output_path
                click.echo(f"Renamed output file to: {new_output_path.name}")
            except Exception as e:
                click.echo(f"Error renaming output file: {e}", err=True)
    
    return result

