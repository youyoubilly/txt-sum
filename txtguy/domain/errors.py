"""Domain errors for txtguy."""


class TxtSumError(Exception):
    """Base exception for all txtguy errors."""
    pass


class ConfigError(TxtSumError):
    """Configuration-related errors."""
    pass


class ParseError(TxtSumError):
    """File parsing errors."""
    pass


class ProviderError(TxtSumError):
    """LLM provider errors."""
    pass


class ContentTooLongError(TxtSumError):
    """Content exceeds maximum length."""
    
    def __init__(self, content_length: int, max_length: int, file_name: str = ""):
        self.content_length = content_length
        self.max_length = max_length
        self.file_name = file_name
        message = (
            f"Content too long: {content_length} characters exceeds "
            f"maximum limit of {max_length} characters"
        )
        if file_name:
            message = f"File '{file_name}': {message}"
        super().__init__(message)

