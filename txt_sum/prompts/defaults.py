"""Default prompt templates."""

DEFAULT_PROMPTS = {
    "default": (
        "Please summarize the following content in a clear and concise manner.\n"
        "Focus on the main themes, key events, and important information.\n\n"
        "Content:\n{content}"
    ),
    "detailed": (
        "Provide a detailed summary of the following content with:\n"
        "1. Overview\n"
        "2. Key Themes\n"
        "3. Important Events\n"
        "4. Main Points\n\n"
        "Content:\n{content}"
    ),
    "brief": (
        "Create a brief summary (2-3 sentences) of the following content:\n\n"
        "{content}"
    ),
}

