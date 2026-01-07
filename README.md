# txt-sum

> **Smart text file summarization using LLM APIs**

A Python command-line tool to summarize text files using LLM APIs. Supports subtitle formats (SRT, TXT, VTT, ASS/SSA) and any text-based file. Perfect for quickly understanding the content of video subtitles, transcripts, dialogue files, documents, and more.

> **Note**: This tool was primarily developed with AI assistance (vibe coding), starting from initial concepts and requirements by Billy Wang. While the code has been tested and is functional, users are advised to use it at their own discretion and responsibility. Please review the code and test thoroughly for your specific use cases.

## Features

- **Any Text File Support**: Process subtitle formats (SRT, TXT, VTT, ASS/SSA) and any text-based file
- **Smart Formatting Removal**: Automatically strips timestamps and formatting from subtitle files to reduce text size
- **LLM Integration**: Works with local LLM servers (LM Studio) and cloud APIs (OpenAI, Alibaba Qwen - coming soon)
- **Configurable Prompts**: Customize summarization style with prompt templates stored in `~/.txt-sum/prompts.yaml`
- **Batch Processing**: Process multiple files at once
- **Text Length Limits**: Automatically skips files that exceed configurable length limits
- **Filename Suggestions**: AI-powered filename recommendations with interactive selection
- **Easy Configuration**: Simple YAML-based configuration stored in `~/.txt-sum/`

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/youyoubilly/txt-sum.git
cd txt-sum

# Install the package
pip install -e .
```

### From PyPI (when published)

```bash
pip install txt-sum
```

## Quick Start

1. **Initialize Configuration**

   ```bash
   txt-sum --init-config
   ```

   This creates configuration files at:
   - `~/.txt-sum/config.yaml` - LLM provider settings
   - `~/.txt-sum/prompts.yaml` - Prompt templates

2. **Edit Configuration**

   Open `~/.txt-sum/config.yaml` and configure your LLM provider:

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
   txt-sum movie.srt
   ```

   This creates `movie.md` in the same directory as the input file.

## Usage

### Basic Usage

```bash
# Single file
txt-sum input.srt

# Multiple files (batch processing)
txt-sum file1.srt file2.txt file3.vtt

# Process all text files in a folder
txt-sum /path/to/files/

# Mix files and folders
txt-sum file1.srt /path/to/folder/ file2.txt

# Process any text file (not just subtitles)
txt-sum document.txt --force-text

# Specify output file
txt-sum input.srt -o summary.md

# Use a specific prompt template
txt-sum input.srt -p detailed

# Specify summary language (default: en)
txt-sum input.srt -l en
txt-sum input.srt -l zh  # Chinese
txt-sum input.srt -l es  # Spanish

# Add additional context (direct text)
txt-sum call.srt -c "this is a sale call from api provider to a company manager"

# Add additional context (from file)
txt-sum call.srt -c extra-context.txt

# Process folder with force (overwrite existing outputs)
txt-sum /path/to/files/ --force

# Override LLM provider
txt-sum input.srt --provider lm_studio

# Preserve timestamps and formatting (for subtitle files)
txt-sum input.srt --full-context

# Suggest better filenames after summarization
txt-sum input.srt --suggest-filenames
```

### Command Options

- `-o, --output PATH`: Output file path (single file) or directory (multiple files)
- `-p, --prompt-template NAME`: Use a specific prompt template
- `-l, --language CODE`: Language code for the summary (default: en). Examples: en, zh, es, fr, de, ja, ko
- `-c, --context TEXT_OR_FILE`: Additional context to help with summarization. Can be direct text or a file path
- `-f, --force`: Force processing even if output file already exists (overwrite existing files)
- `--force-text`: Force processing of unknown file types (attempt to process as text)
- `--full-context`: Process subtitle files with full context (preserve timestamps and formatting)
- `--suggest-filenames`: After summarization, suggest better filenames using LLM
- `--provider PROVIDER`: Override LLM provider (lm_studio, openai, qwen)
- `--config PATH`: Use a custom config file
- `--init-config`: Initialize config and prompts files in default location
- `-v, --verbose`: Verbose output
- `-h, --help`: Show help message

## Configuration

Configuration files are located in `~/.txt-sum/`:
- `config.yaml` - LLM provider settings and general configuration
- `prompts.yaml` - Prompt templates for summarization

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
prompts_file: ~/.txt-sum/prompts.yaml
```

**prompts.yaml:**
```yaml
templates:
  default: |
    Please summarize the following content in a clear and concise manner.
    Focus on the main themes, key events, and important information.
    
    Content:
    {content}
  detailed: |
    Provide a detailed summary of the following content with:
    1. Overview
    2. Key Themes
    3. Important Events
    4. Main Points
    
    Content:
    {content}
  brief: |
    Create a brief summary (2-3 sentences) of the following content:
    
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

### Adding Custom Prompt Templates

Edit `~/.txt-sum/prompts.yaml` and add your template under `templates`:

```yaml
templates:
  my_custom_template: |
    Your custom prompt here.
    Use {content} as a placeholder for the text content.
    
    {content}
```

Then use it with:

```bash
txt-sum input.srt -p my_custom_template
```

**Note**: Prompt templates are stored separately in `prompts.yaml` for easy editing and reuse across different virtual environments and computers.

### Using Additional Context

The `-c/--context` flag allows you to provide additional context that helps the LLM generate better summaries. This is especially useful when:

- The subtitle content needs domain-specific understanding (e.g., technical calls, medical transcripts)
- You want to focus on specific aspects (e.g., "focus on pricing discussions")
- The content has background information that's not in the subtitles

**Examples:**

```bash
# Provide context as direct text
txt-sum meeting.srt -c "This is a product planning meeting. Focus on feature requirements and timeline discussions."

# Provide context from a file
txt-sum interview.srt -c interview-background.txt
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

### Coming Soon

- **OpenAI**: GPT-3.5, GPT-4, etc.
- **Alibaba Qwen**: Qwen models via DashScope API

## Examples

### Example 1: Quick Summary

```bash
txt-sum episode.srt
```

Output: `episode.md` with a summary of the episode.

### Example 2: Detailed Summary with Custom Output

```bash
txt-sum movie.srt -o ~/Documents/movie_summary.md -p detailed
```

### Example 3: Batch Process Multiple Files

```bash
txt-sum episode1.srt episode2.srt episode3.srt -o ~/summaries/
```

All summaries will be saved in `~/summaries/` directory.

### Example 4: Process Any Text File

```bash
txt-sum document.txt
txt-sum logfile.log --force-text
txt-sum code.py --force-text
```

### Example 5: With Filename Suggestions

```bash
txt-sum input.srt --suggest-filenames
```

The tool will suggest better filenames and ask for confirmation.

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

- Run `txt-sum --init-config` to create fresh config and prompts files
- Check YAML syntax in `~/.txt-sum/config.yaml` and `~/.txt-sum/prompts.yaml`
- Verify all required fields are present

### File Length Limits

- Files exceeding the maximum text length (default: 100,000 characters) are automatically skipped
- Adjust `max_text_length` in `config.yaml` to change the limit
- Skipped files are reported at the end of batch processing

## Development

### Project Structure

```
txt-sum/
├── docs/
│   └── architecture.md     # Architecture documentation with diagrams
├── txt_sum/
│   ├── cli.py              # CLI interface
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
│   │   └── output.py       # Output formatting
│   ├── utils/              # Utility modules
│   │   ├── file_utils.py   # File operations
│   │   ├── text_utils.py   # Text processing
│   │   └── cli_utils.py    # CLI helpers
│   ├── prompts/            # Prompt management
│   │   ├── manager.py      # Prompt manager
│   │   └── defaults.py     # Default prompts
│   └── llm/                # LLM provider layer
│       ├── registry.py     # Provider registry
│       └── providers/      # Provider implementations
│           ├── base.py     # Base provider class
│           ├── lm_studio.py    # LM Studio
│           ├── qwen.py     # Alibaba Qwen
│           └── openai.py   # OpenAI
├── tests/                  # Test suite
│   ├── test_chunking.py
│   ├── test_sanitize.py
│   ├── test_parser.py
│   └── test_provider_registry.py
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
pytest --cov=txt_sum

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
   - New LLM providers go in `txt_sum/llm/providers/`
   - Register new providers in `txt_sum/llm/registry.py`
   - Add tests for new functionality

4. **Add a new LLM provider:**
   ```python
   # 1. Create txt_sum/llm/providers/my_provider.py
   from txt_sum.llm.providers.base import BaseLLMProvider
   
   class MyProvider(BaseLLMProvider):
       def validate_config(self):
           # Validation logic
           return True
       
       def generate(self, prompt, content, **kwargs):
           # Implementation
           return summary
   
   # 2. Register in txt_sum/llm/registry.py
   from txt_sum.llm.providers.my_provider import MyProvider
   
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

