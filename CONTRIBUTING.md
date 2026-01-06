# Contributing to SRT Summarizor

Thank you for your interest in contributing to SRT Summarizor! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Any relevant error messages or logs
- Sample subtitle file (if applicable, anonymized if needed)

### Suggesting Features

We welcome feature suggestions! Please open an issue describing:
- The feature you'd like to see
- Why it would be useful
- How it might work
- Any potential implementation considerations

### Pull Requests

1. **Fork the repository** and create a new branch for your changes
2. **Make your changes** following the code style of the project
3. **Test your changes** to ensure they work correctly with different subtitle formats
4. **Update documentation** if needed (README, docstrings, etc.)
5. **Submit a pull request** with a clear description of your changes

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/youyoubilly/srt-summarizor.git
   cd srt-summarizor
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

3. Test the installation:
   ```bash
   srt-summarizor --help
   ```

## Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular
- Use type hints where appropriate

## Testing

Before submitting a PR, please test your changes:
- Test with different subtitle formats (SRT, TXT, VTT, ASS/SSA)
- Test with various file encodings
- Test with different LLM providers (if applicable)
- Ensure existing functionality still works
- Test batch processing if you modified related code

## Areas for Contribution

- **New LLM Providers**: Add support for additional LLM APIs (OpenAI, Qwen, etc.)
- **Subtitle Format Support**: Add parsers for additional subtitle formats
- **Prompt Templates**: Share useful prompt templates
- **Documentation**: Improve documentation, add examples, fix typos
- **Bug Fixes**: Fix issues reported in the issue tracker
- **Performance**: Optimize parsing or processing speed
- **Error Handling**: Improve error messages and handling

## Questions?

Feel free to open an issue if you have questions about contributing!

