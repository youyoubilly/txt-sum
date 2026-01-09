# txtguy

> **A versatile text processing tool with LLM integration**

A Python command-line tool for processing text files using LLM APIs. Supports summarization with multiple format options (short, long, blog-style), filename suggestions, and more. Works with subtitle formats (SRT, TXT, VTT, ASS/SSA) and any text-based file. Perfect for quickly understanding content, organizing files, and creating structured summaries.

> **Note**: This tool was primarily developed with AI assistance (vibe coding), starting from initial concepts and requirements by Billy Wang. While the code has been tested and is functional, users are advised to use it at their own discretion and responsibility. Please review the code and test thoroughly for your specific use cases.

## Features

- **Subcommand Architecture**: Modular design with `summarize`, `rename`, `template`, and `config` subcommands
- **Multiple Summary Formats**: Choose from short, long, or blog-style summaries via template categories
- **Template System**: Categorized templates (short/long/blog) with custom template support
- **Any Text File Support**: Process subtitle formats (SRT, TXT, VTT, ASS/SSA) and any text-based file
- **Smart Formatting Removal**: Automatically strips timestamps and formatting from subtitle files to reduce text size
- **LLM Integration**: Works with local LLM servers (LM Studio) and cloud APIs (OpenAI, Alibaba Qwen)
- **Filename Suggestions**: AI-powered filename recommendations with interactive selection
- **Batch Processing**: Process multiple files at once
- **Text Length Limits**: Automatically skips files that exceed configurable length limits
- **Easy Configuration**: Simple YAML-based configuration stored in `~/.txtguy/`

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/youyoubilly/txt-sum.git
cd txt-sum

# Install the package in development mode
pip install -e .
```

### From PyPI (when published)

```bash
pip install txtguy
```

## Quick Start

1. **Initialize Configuration**

   ```bash
   txtguy config init
   ```

   This creates configuration files at:
   - `~/.txtguy/config.yaml` - LLM provider settings
   - `~/.txtguy/templates.yaml` - Template categories and custom templates

2. **Edit Configuration**

   Open `~/.txtguy/config.yaml` and configure your LLM provider:

   ```yaml
   llm_provider: lm_studio
   llm_settings:
     lm_studio:
       base_url: http://localhost:1234/v1
       api_key: ""
       model: ""
   ```

3. **Start LM Studio** (if using local LLM)

   - Open LM Studio
   - Load a model
   - Start the local server (usually on port 1234)

4. **Summarize a File**

   ```bash
   txtguy summarize movie.srt
   ```

   This creates `movie.md` in the same directory as the input file.

## Usage

### Summarize Subcommand

The `summarize` subcommand handles text file summarization with multiple format options.

#### Basic Usage

```bash
# Single file
txtguy summarize input.srt

# Multiple files (batch processing)
txtguy summarize file1.srt file2.txt file3.vtt

# Process all text files in a folder
txtguy summarize /path/to/files/

# Mix files and folders
txtguy summarize file1.srt /path/to/folder/ file2.txt

# Process any text file (not just subtitles)
txtguy summarize document.txt --force-text

# Specify output file
txtguy summarize input.srt -o summary.md
```

#### Format Options

```bash
# Use short format (brief summary)
txtguy summarize input.srt --format short

# Use long format (detailed summary)
txtguy summarize input.srt --format long

# Use blog format (blog-style article)
txtguy summarize input.srt --format blog

# Use a specific template by name
txtguy summarize input.srt --template my_custom_template

# Use a template from a specific category
txtguy summarize input.srt --template default --category short
```

#### Advanced Options

```bash
# Specify summary language (default: en)
txtguy summarize input.srt -l en
txtguy summarize input.srt -l zh  # Chinese
txtguy summarize input.srt -l es  # Spanish

# Add additional context (direct text)
txtguy summarize call.srt -c "this is a sale call from api provider to a company manager"

# Add additional context (from file)
txtguy summarize call.srt -c extra-context.txt

# Process folder with force (overwrite existing outputs)
txtguy summarize /path/to/files/ --force

# Override LLM provider
txtguy summarize input.srt --provider lm_studio

# Preserve timestamps and formatting (for subtitle files)
txtguy summarize input.srt --full-context

# Verbose output
txtguy summarize input.srt -v
```

### Rename Subcommand

The `rename` subcommand suggests and renames files based on their content.

```bash
# Suggest filenames based on file content
txtguy rename file.srt

# Use existing summary file for better suggestions
txtguy rename file.srt --with-summary summary.md

# Batch rename multiple files
txtguy rename *.srt

# Verbose output
txtguy rename file.srt -v
```

### Template Subcommand

The `template` subcommand manages template categories and custom templates.

```bash
# List all templates and categories
txtguy template list

# List templates in a specific category
txtguy template list --category short

# Show template content
txtguy template show default

# Show template from a category
txtguy template show default --category short

# Create a new template
txtguy template create my_template

# Create a template in a category
txtguy template create my_template --category short
```

### Config Subcommand

The `config` subcommand manages configuration.

```bash
# Show current configuration
txtguy config show

# Initialize configuration files
txtguy config init
```

## Configuration

Configuration files are located in `~/.txtguy/`:
- `config.yaml` - LLM provider settings and general configuration
- `templates.yaml` - Template categories and custom templates

### Default Configuration Structure

**config.yaml:**
```yaml
default_output_path: ~/Documents/summaries
llm_provider: lm_studio
llm_settings:
  lm_studio:
    base_url: http://localhost:1234/v1
    api_key: ""
    model: ""
  openai:
    api_key: ""
    model: "gpt-3.5-turbo"
  qwen:
    api_key: ""
    model: "qwen-turbo"
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
default_prompt_template: default
max_text_length: 100000
templates_file: ~/.txtguy/templates.yaml
```

**templates.yaml:**
```yaml
categories:
  short:
    default: |
      Create a brief summary (2-3 sentences) of the following content.
      Focus on the main point and key information.
      
      Content:
      {content}
    concise: |
      Create a one-sentence summary of the following content:
      
      {content}
  
  long:
    default: |
      Provide a detailed summary of the following content with:
      1. Overview
      2. Key Themes
      3. Important Events
      4. Main Points
      5. Conclusion
      
      Content:
      {content}
  
  blog:
    default: |
      Write a blog-style article based on the following content.
      Include:
      - An engaging introduction that hooks the reader
      - Well-organized main content sections with clear headings
      - A compelling conclusion
      - Natural, conversational tone
      
      Content:
      {content}

custom:
  my_template: |
    Your custom prompt here.
    Use {content} as a placeholder for the text content.
    
    {content}
```

### Configuring LM Studio

1. Install and open [LM Studio](https://lmstudio.ai/)
2. Download and load a model
3. Start the local server (usually runs on `http://localhost:1234`)
4. Update your config:

   ```yaml
   llm_provider: lm_studio
   llm_settings:
     lm_studio:
       base_url: http://localhost:1234/v1
   ```

### Template Categories

txtguy comes with three default template categories:

- **short**: Brief summaries (2-3 sentences or one sentence)
- **long**: Detailed summaries with structured sections
- **blog**: Blog-style articles with engaging introductions and conclusions

Each category has a `default` template, and you can add more templates to any category.

### Adding Custom Templates

You can add custom templates in two ways:

1. **Using the CLI:**
   ```bash
   txtguy template create my_template
   txtguy template create my_template --category short
   ```

2. **Editing templates.yaml directly:**
   ```yaml
   categories:
     short:
       my_custom: |
         Your custom prompt here.
         {content}
   
   custom:
     my_standalone_template: |
       Another custom template.
       {content}
   ```

Then use them with:
```bash
txtguy summarize input.srt --template my_custom --category short
txtguy summarize input.srt --template my_standalone_template
```

### Using Additional Context

The `-c/--context` flag allows you to provide additional context that helps the LLM generate better summaries. This is especially useful when:

- The subtitle content needs domain-specific understanding (e.g., technical calls, medical transcripts)
- You want to focus on specific aspects (e.g., "focus on pricing discussions")
- The content has background information that's not in the subtitles

**Examples:**

```bash
# Provide context as direct text
txtguy summarize meeting.srt -c "This is a product planning meeting. Focus on feature requirements and timeline discussions."

# Provide context from a file
txtguy summarize interview.srt -c interview-background.txt
```

The context file can contain any relevant information:
- Background about participants
- Domain-specific terminology
- Focus areas or key points to emphasize
- Any other context that helps understand the content

The context is appended to the prompt template, so the LLM can use it to generate more accurate and relevant summaries.

## Supported File Formats

### Subtitle Formats (with specialized parsing)
- **SRT** (`.srt`): SubRip subtitle format
- **TXT** (`.txt`): Plain text files
- **VTT** (`.vtt`): WebVTT format
- **ASS/SSA** (`.ass`, `.ssa`): Advanced SubStation Alpha format

### Any Text File
- The tool can process **any text-based file** by default
- Binary files are automatically detected and skipped (use `--force-text` to attempt processing)
- Timestamps and formatting are automatically removed from subtitle files to reduce text size
- Use `--full-context` to preserve timestamps and formatting when needed

## LLM Providers

### Currently Supported

- **LM Studio**: Local LLM server (OpenAI-compatible API)
- **OpenAI**: GPT-3.5, GPT-4, etc.
- **Alibaba Qwen**: Qwen models via DashScope API

## Examples

### Example 1: Quick Summary

```bash
txtguy summarize episode.srt
```

Output: `episode.md` with a summary of the episode.

### Example 2: Short Format Summary

```bash
txtguy summarize episode.srt --format short
```

Output: A brief 2-3 sentence summary.

### Example 3: Blog-Style Article

```bash
txtguy summarize movie.srt --format blog
```

Output: A blog-style article with engaging introduction and structured content.

### Example 4: Detailed Summary with Custom Output

```bash
txtguy summarize movie.srt -o ~/Documents/movie_summary.md --format long
```

### Example 5: Batch Process Multiple Files

```bash
txtguy summarize episode1.srt episode2.srt episode3.srt -o ~/summaries/
```

All summaries will be saved in `~/summaries/` directory.

### Example 6: Process Any Text File

```bash
txtguy summarize document.txt
txtguy summarize logfile.log --force-text
txtguy summarize code.py --force-text
```

### Example 7: Rename Files with AI Suggestions

```bash
txtguy rename file.srt
```

The tool will analyze the file content and suggest better filenames.

### Example 8: Using Custom Templates

```bash
# Create a custom template
txtguy template create technical_summary

# Use it
txtguy summarize meeting.srt --template technical_summary
```

## Migration from txt-sum

If you were using the previous `txt-sum` tool, your configuration will be automatically migrated to `~/.txtguy/` the first time you run txtguy. The old `~/.txt-sum/` directory will remain as a backup.

## Troubleshooting

### Connection Error with LM Studio

- Make sure LM Studio is running
- Verify the server is started (check the "Local Server" tab in LM Studio)
- Check that the `base_url` in your config matches the server URL
- Default is `http://localhost:1234/v1`

### Empty or Invalid Subtitle File

- Verify the file format is supported
- Check file encoding (tool auto-detects, but UTF-8 is recommended)
- Ensure the file contains actual subtitle content

### Configuration Issues

- Run `txtguy config init` to create fresh config and templates files
- Check YAML syntax in `~/.txtguy/config.yaml` and `~/.txtguy/templates.yaml`
- Verify all required fields are present

### File Length Limits

- Files exceeding the maximum text length (default: 100,000 characters) are automatically skipped
- Adjust `max_text_length` in `config.yaml` to change the limit
- Skipped files are reported at the end of batch processing

### Template Not Found

- Use `txtguy template list` to see all available templates
- Check if you're using the correct category with `--category` flag
- Verify template names are spelled correctly

## Development

### Project Structure

```
txtguy/
├── docs/
│   └── architecture.md     # Architecture documentation with diagrams
├── txtguy/
│   ├── cli/                # CLI subcommands
│   │   ├── __init__.py     # Main CLI group
│   │   ├── summarize.py    # Summarize subcommand
│   │   ├── rename.py       # Rename subcommand
│   │   ├── template.py     # Template management
│   │   ├── config.py       # Config management
│   │   └── base.py         # Base subcommand class
│   ├── cli.py              # Legacy CLI (backward compatibility)
│   ├── config.py           # Configuration management
│   ├── parser.py           # Text file parsers
│   ├── summarizer.py       # Backward-compatible wrapper
│   ├── domain/             # Domain layer (types, errors)
│   │   ├── types.py        # Core data types
│   │   └── errors.py       # Typed exceptions
│   ├── app/                # Application layer (use cases)
│   │   ├── summarize.py    # Main orchestration
│   │   ├── chunking.py     # Content chunking
│   │   ├── sanitize.py     # Response cleanup
│   │   ├── output.py       # Output formatting
│   │   └── filename_suggest.py  # Filename suggestions
│   ├── utils/              # Utility modules
│   │   ├── file_utils.py   # File operations
│   │   ├── text_utils.py   # Text processing
│   │   └── cli_utils.py    # CLI helpers
│   ├── prompts/            # Template management
│   │   ├── manager.py      # Template manager
│   │   ├── categories.py   # Default category templates
│   │   └── defaults.py     # Legacy default templates
│   └── llm/                # LLM provider layer
│       ├── registry.py     # Provider registry
│       └── providers/      # Provider implementations
│           ├── base.py      # Base provider class
│           ├── lm_studio.py # LM Studio
│           ├── qwen.py      # Alibaba Qwen
│           └── openai.py    # OpenAI
├── tests/                   # Test suite
│   ├── test_chunking.py
│   ├── test_sanitize.py
│   ├── test_parser.py
│   ├── test_provider_registry.py
│   └── test_filename_suggest.py
├── pyproject.toml          # Package configuration
└── README.md               # This file
```

For detailed architecture documentation and design decisions, see [docs/architecture.md](docs/architecture.md).

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov=txtguy

# Run specific test file
pytest tests/test_chunking.py

# Run with verbose output
pytest -v
```

### Development Workflow

1. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Run tests before committing:**
   ```bash
   pytest
   ```

3. **Check code structure:**
   - See `docs/architecture.md` for architecture guidelines
   - New LLM providers go in `txtguy/llm/providers/`
   - Register new providers in `txtguy/llm/registry.py`
   - Add tests for new functionality

4. **Add a new subcommand:**
   ```python
   # 1. Create txtguy/cli/my_subcommand.py
   import click
   from txtguy.cli.base import BaseSubcommand
   
   @click.command()
   def my_subcommand():
       """My new subcommand."""
       # Implementation
       pass
   
   # 2. Register in txtguy/cli/__init__.py
   from txtguy.cli.my_subcommand import my_subcommand
   cli.add_command(my_subcommand)
   ```

5. **Add a new LLM provider:**
   ```python
   # 1. Create txtguy/llm/providers/my_provider.py
   from txtguy.llm.providers.base import BaseLLMProvider
   
   class MyProvider(BaseLLMProvider):
       def validate_config(self):
           # Validation logic
           return True
       
       def generate(self, prompt, content, **kwargs):
           # Implementation
           return summary
   
   # 2. Register in txtguy/llm/registry.py
   from txtguy.llm.providers.my_provider import MyProvider
   
   _providers = {
       "my_provider": MyProvider,
       # ... existing providers
   }
   ```

## License

MIT License

## Disclaimer

This software is provided "as is" without warranty of any kind. This tool was developed with AI assistance (vibe coding) based on initial requirements and concepts by Billy Wang. While efforts have been made to ensure functionality and reliability, users should:

- Review the code before use
- Test thoroughly with their specific subtitle formats and use cases
- Use at their own risk and responsibility
- Not rely on this tool for critical applications without proper validation

The authors and contributors are not responsible for any data loss, incorrect results, or other issues that may arise from using this software.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

## Support

For issues, questions, or feature requests, please open an issue on [GitHub](https://github.com/youyoubilly/txt-sum/issues).

## Author

**Billy Wang** - billy@techxartisan.com
