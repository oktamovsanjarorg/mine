import re
from bs4 import BeautifulSoup

def escape_markdown(text: str) -> str:
    """Escape markdown special characters for Telegram MarkdownV2."""
    escape_chars = r"\_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

def truncate(text: str, max_length: int = 4096, suffix: str = '...') -> str:
    """Truncate text to max_length with a given suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def format_code_block(code: str, language: str = '') -> str:
    """Format text as a markdown code block."""
    return f"```{language}\n{code}\n```"

def strip_html(html: str) -> str:
    """Remove HTML tags from a string."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def slugify(text: str) -> str:
    """Convert text to a slug format."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text

def word_count(text: str) -> int:
    """Count words in a string."""
    words = re.findall(r'\b\w+\b', text)
    return len(words)
