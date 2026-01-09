"""Default template categories for different summary formats."""

DEFAULT_CATEGORIES = {
    "short": {
        "default": (
            "Create a brief summary (2-3 sentences) of the following content.\n"
            "Focus on the main point and key information.\n\n"
            "Content:\n{content}"
        ),
        "concise": (
            "Create a one-sentence summary of the following content:\n\n"
            "{content}"
        ),
    },
    "long": {
        "default": (
            "Provide a detailed summary of the following content with:\n"
            "1. Overview\n"
            "2. Key Themes\n"
            "3. Important Events\n"
            "4. Main Points\n"
            "5. Conclusion\n\n"
            "Content:\n{content}"
        ),
        "structured": (
            "Create a structured summary with the following sections:\n"
            "- Executive Summary\n"
            "- Key Findings\n"
            "- Detailed Analysis\n"
            "- Recommendations (if applicable)\n\n"
            "Content:\n{content}"
        ),
    },
    "blog": {
        "default": (
            "Write a blog-style article based on the following content.\n"
            "Include:\n"
            "- An engaging introduction that hooks the reader\n"
            "- Well-organized main content sections with clear headings\n"
            "- A compelling conclusion\n"
            "- Natural, conversational tone\n\n"
            "Content:\n{content}"
        ),
        "technical": (
            "Write a technical blog post based on the following content.\n"
            "Include:\n"
            "- Clear technical explanations\n"
            "- Code examples or technical details where relevant\n"
            "- Structured sections with headings\n"
            "- Practical insights and takeaways\n\n"
            "Content:\n{content}"
        ),
    },
}

# Legacy templates for backward compatibility
LEGACY_DEFAULT_PROMPTS = {
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
