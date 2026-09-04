def format_number(number: int | float, locale: str = 'uz') -> str:
    """Format number with spaces (e.g. 1 234 567)"""
    return f"{number:,}".replace(",", " ")

def format_currency(amount: int | float, currency: str = 'UZS') -> str:
    """Format currency (e.g. 1 234 567 UZS)"""
    return f"{format_number(amount)} {currency}"

def format_file_size(size_bytes: int) -> str:
    """Format file size (e.g. 1.5 MB)"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}".replace('.0', '')
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def format_duration(minutes: int) -> str:
    """Format duration in minutes to string (e.g. 1 soat 30 min)"""
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0 and mins > 0:
        return f"{hours} soat {mins} min"
    elif hours > 0:
        return f"{hours} soat"
    else:
        return f"{mins} min"

def format_percentage(value: float, total: float) -> str:
    """Format percentage (e.g. 45.5%)"""
    if total == 0:
        return "0%"
    pct = (value / total) * 100
    return f"{pct:.1f}%".replace('.0', '')

def progress_bar(current: int | float, total: int | float, length: int = 20) -> str:
    """Create a textual progress bar (e.g. ████████████░░░░░░░░ 60%)."""
    if total <= 0:
        return "░" * length + " 0%"
    
    ratio = current / total
    ratio = max(0.0, min(1.0, ratio))
    filled = int(length * ratio)
    bar = "█" * filled + "░" * (length - filled)
    return f"{bar} {int(ratio * 100)}%"
