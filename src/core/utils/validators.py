import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """Check if the provided string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def validate_email(email: str) -> bool:
    """Check if the provided string is a valid email format."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Check if the provided string is a valid international phone format."""
    pattern = r'^\+?[\d\s-]{9,15}$'
    return bool(re.match(pattern, phone))

def validate_hex_color(color: str) -> bool:
    """Check if the provided string is a valid hex color code."""
    pattern = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
    return bool(re.match(pattern, color))

def validate_time_format(time_str: str) -> bool:
    """Check if the provided string is in valid HH:MM format."""
    pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, time_str))

def validate_currency_code(code: str) -> bool:
    """Check if the provided string is a valid 3-letter currency code."""
    pattern = r'^[A-Z]{3}$'
    return bool(re.match(pattern, code))

def sanitize_filename(filename: str) -> str:
    """Sanitize string to be used as a valid filename."""
    return re.sub(r'[^\w\-_\. ]', '_', filename)
