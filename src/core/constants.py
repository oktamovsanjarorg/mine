MAX_TELEGRAM_MESSAGE_LENGTH = 4096
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50

EMOJI = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "settings": "⚙️",
    "user": "👤",
    "calendar": "📅",
    "time": "⏰",
    "water": "💧",
    "sleep": "😴",
    "pomodoro": "🍅",
    "money": "💰",
    "stats": "📊",
    "file": "📄"
}

DATE_FORMAT = "%d.%m.%Y"
DATETIME_FORMAT = "%d.%m.%Y %H:%M"
TIME_FORMAT = "%H:%M"

SUPPORTED_FILE_TYPES = [
    "image/jpeg",
    "image/png",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

AI_MAX_CONTEXT_MESSAGES = 20
AI_MAX_CONTEXT_TOKENS = 8000

POMODORO = {
    "work": 25,
    "short_break": 5,
    "long_break": 15,
    "sessions": 4
}

WATER_DAILY_TARGET = 2000  # ml
SLEEP_TARGET = 8.0  # hours
