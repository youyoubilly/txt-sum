# SRT Summarizor

> **Smart subtitle summarization using LLM APIs**

A Python command-line tool to summarize subtitle files (SRT, TXT, VTT, ASS/SSA) using LLM APIs. Perfect for quickly understanding the content of video subtitles, transcripts, or dialogue files.

> **Note**: This tool was primarily developed with AI assistance (vibe coding), starting from initial concepts and requirements by Billy Wang. While the code has been tested and is functional, users are advised to use it at their own discretion and responsibility. Please review the code and test thoroughly for your specific use cases.

## Features

- **Multiple Subtitle Formats**: Supports SRT, TXT, VTT, and ASS/SSA formats
- **LLM Integration**: Works with local LLM servers (LM Studio) and cloud APIs (OpenAI, Alibaba Qwen - coming soon)
- **Configurable Prompts**: Customize summarization style with prompt templates
- **Batch Processing**: Process multiple files at once
- **Easy Configuration**: Simple YAML-based configuration stored in `~/.srt-summarizor/`

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/youyoubilly/srt-summarizor.git
cd srt-summarizor

# Install the package
pip install -e .
```

### From PyPI (when published)

```bash
pip install srt-summarizor
```

## Quick Start

1. **Initialize Configuration**

   ```bash
   srt-summarizor --init-config
   ```

   This creates a configuration file at `~/.srt-summarizor/config.yaml`.

2. **Edit Configuration**

   Open `~/.srt-summarizor/config.yaml` and configure your LLM provider:

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
   srt-summarizor movie.srt
   ```

   This creates `movie.md` in the same directory as the input file.

## Usage

### Basic Usage

```bash
# Single file
srt-summarizor input.srt

# Multiple files (batch processing)
srt-summarizor file1.srt file2.txt file3.vtt

# Process all subtitle files in a folder
srt-summarizor /path/to/subtitles/

# Mix files and folders
srt-summarizor file1.srt /path/to/folder/ file2.srt

# Specify output file
srt-summarizor input.srt -o summary.md

# Use a specific prompt template
srt-summarizor input.srt -p detailed

# Specify summary language (default: en)
srt-summarizor input.srt -l en
srt-summarizor input.srt -l zh  # Chinese
srt-summarizor input.srt -l es  # Spanish

# Add additional context (direct text)
srt-summarizor call.srt -c "this is a sale call from api provider to a company manager"

# Add additional context (from file)
srt-summarizor call.srt -c extra-context.txt

# Process folder with force (overwrite existing outputs)
srt-summarizor /path/to/subtitles/ --force

# Override LLM provider
srt-summarizor input.srt --provider lm_studio
```

### Command Options

- `-o, --output PATH`: Output file path (single file) or directory (multiple files)
- `-p, --prompt-template NAME`: Use a specific prompt template
- `-l, --language CODE`: Language code for the summary (default: en). Examples: en, zh, es, fr, de, ja, ko
- `-c, --context TEXT_OR_FILE`: Additional context to help with summarization. Can be direct text or a file path
- `-f, --force`: Force processing even if output file already exists (overwrite existing files)
- `--provider PROVIDER`: Override LLM provider (lm_studio, openai, qwen)
- `--config PATH`: Use a custom config file
- `--init-config`: Initialize config file in default location
- `-v, --verbose`: Verbose output
- `-h, --help`: Show help message

## Configuration

The configuration file is located at `~/.srt-summarizor/config.yaml`.

### Default Configuration Structure

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
prompt_templates:
  default: |
    Please summarize the following subtitle content in a clear and concise manner.
    Focus on the main themes, key events, and important dialogue.
    
    Subtitle content:
    {content}
  detailed: |
    Provide a detailed summary of the following subtitle content with:
    1. Overview
    2. Key Themes
    3. Important Events
    4. Character Interactions
    
    Subtitle content:
    {content}
  brief: |
    Create a brief summary (2-3 sentences) of the following subtitle content:
    
    {content}
default_prompt_template: default
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

Edit `~/.srt-summarizor/config.yaml` and add your template under `prompt_templates`:

```yaml
prompt_templates:
  my_custom_template: |
    Your custom prompt here.
    Use {content} as a placeholder for the subtitle content.
    
    {content}
```

Then use it with:

```bash
srt-summarizor input.srt -p my_custom_template
```

### Using Additional Context

The `-c/--context` flag allows you to provide additional context that helps the LLM generate better summaries. This is especially useful when:

- The subtitle content needs domain-specific understanding (e.g., technical calls, medical transcripts)
- You want to focus on specific aspects (e.g., "focus on pricing discussions")
- The content has background information that's not in the subtitles

**Examples:**

```bash
# Provide context as direct text
srt-summarizor meeting.srt -c "This is a product planning meeting. Focus on feature requirements and timeline discussions."

# Provide context from a file
srt-summarizor interview.srt -c interview-background.txt
```

The context file can contain any relevant information:
- Background about participants
- Domain-specific terminology
- Focus areas or key points to emphasize
- Any other context that helps understand the content

The context is appended to the prompt template, so the LLM can use it to generate more accurate and relevant summaries.

## Supported File Formats

- **SRT** (`.srt`): SubRip subtitle format
- **TXT** (`.txt`): Plain text files
- **VTT** (`.vtt`): WebVTT format
- **ASS/SSA** (`.ass`, `.ssa`): Advanced SubStation Alpha format

## LLM Providers

### Currently Supported

- **LM Studio**: Local LLM server (OpenAI-compatible API)

### Coming Soon

- **OpenAI**: GPT-3.5, GPT-4, etc.
- **Alibaba Qwen**: Qwen models via DashScope API

## Examples

### Example 1: Quick Summary

```bash
srt-summarizor episode.srt
```

Output: `episode.md` with a summary of the episode.

### Example 2: Detailed Summary with Custom Output

```bash
srt-summarizor movie.srt -o ~/Documents/movie_summary.md -p detailed
```

### Example 3: Batch Process Multiple Files

```bash
srt-summarizor episode1.srt episode2.srt episode3.srt -o ~/summaries/
```

All summaries will be saved in `~/summaries/` directory.

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

- Run `srt-summarizor --init-config` to create a fresh config file
- Check YAML syntax in `~/.srt-summarizor/config.yaml`
- Verify all required fields are present

## Development

### Project Structure

```
srt-summarizor/
├── srt_summarizor/
│   ├── cli.py              # CLI interface
│   ├── config.py           # Configuration management
│   ├── parser.py           # Subtitle file parsers
│   ├── summarizer.py       # Main summarization logic
│   └── llm/
│       ├── base.py         # LLM provider base class
│       └── lm_studio.py    # LM Studio implementation
├── pyproject.toml          # Package configuration
└── README.md               # This file
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
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

For issues, questions, or feature requests, please open an issue on [GitHub](https://github.com/youyoubilly/srt-summarizor/issues).

## Author

**Billy Wang** - billy@techxartisan.com

