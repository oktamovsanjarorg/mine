from datetime import datetime, date, timedelta
import zoneinfo
import re

def now_tz(timezone: str = 'Asia/Tashkent') -> datetime:
    """Get the current datetime in a specific timezone."""
    tz = zoneinfo.ZoneInfo(timezone)
    return datetime.now(tz)

def parse_datetime(text: str, timezone: str = 'Asia/Tashkent') -> datetime | None:
    """Parse relative datetime strings like '30m', '2h', '3d', or 'ertaga 10:00'."""
    text = text.strip().lower()
    now = now_tz(timezone)
    
    # Parse relative minutes
    m_match = re.match(r'^(\d+)m$', text)
    if m_match:
        return now + timedelta(minutes=int(m_match.group(1)))
        
    # Parse relative hours
    h_match = re.match(r'^(\d+)h$', text)
    if h_match:
        return now + timedelta(hours=int(h_match.group(1)))
        
    # Parse relative days
    d_match = re.match(r'^(\d+)d$', text)
    if d_match:
        return now + timedelta(days=int(d_match.group(1)))
        
    # Parse specific string 'ertaga HH:MM'
    ertaga_match = re.match(r'^ertaga\s+(\d{1,2}):(\d{2})$', text)
    if ertaga_match:
        hour, minute = map(int, ertaga_match.groups())
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
    return None

def format_datetime(dt: datetime, format: str = '%d.%m.%Y %H:%M') -> str:
    """Format a datetime object to a string."""
    return dt.strftime(format)

def format_date(d: date, format: str = '%d.%m.%Y') -> str:
    """Format a date object to a string."""
    return d.strftime(format)

def format_relative(dt: datetime) -> str:
    """Format a datetime object relative to now (e.g. '5 daqiqa oldin')."""
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    diff = now - dt
    if diff.total_seconds() < 0:
        return "kelajakda"
    if diff.total_seconds() < 60:
        return f"{int(diff.total_seconds())} soniya oldin"
    if diff.total_seconds() < 3600:
        return f"{int(diff.total_seconds() // 60)} daqiqa oldin"
    if diff.total_seconds() < 86400:
        return f"{int(diff.total_seconds() // 3600)} soat oldin"
    if diff.days == 1:
        return "kecha"
    return f"{diff.days} kun oldin"

def get_start_of_day(dt: datetime, timezone: str = 'Asia/Tashkent') -> datetime:
    """Get the start of the day for a given datetime."""
    tz = zoneinfo.ZoneInfo(timezone)
    return dt.astimezone(tz).replace(hour=0, minute=0, second=0, microsecond=0)

def get_start_of_week(dt: datetime, timezone: str = 'Asia/Tashkent') -> datetime:
    """Get the start of the week for a given datetime."""
    start_of_day = get_start_of_day(dt, timezone)
    return start_of_day - timedelta(days=start_of_day.weekday())

def get_start_of_month(dt: datetime, timezone: str = 'Asia/Tashkent') -> datetime:
    """Get the start of the month for a given datetime."""
    return get_start_of_day(dt, timezone).replace(day=1)

def get_start_of_year(dt: datetime, timezone: str = 'Asia/Tashkent') -> datetime:
    """Get the start of the year for a given datetime."""
    return get_start_of_day(dt, timezone).replace(month=1, day=1)

def days_between(dt1: datetime, dt2: datetime) -> int:
    """Calculate absolute number of days between two datetimes."""
    return abs((dt1.date() - dt2.date()).days)

def is_today(dt: datetime, timezone: str = 'Asia/Tashkent') -> bool:
    """Check if the given datetime is today in the provided timezone."""
    tz = zoneinfo.ZoneInfo(timezone)
    now = datetime.now(tz)
    return dt.astimezone(tz).date() == now.date()

def is_yesterday(dt: datetime, timezone: str = 'Asia/Tashkent') -> bool:
    """Check if the given datetime is yesterday in the provided timezone."""
    tz = zoneinfo.ZoneInfo(timezone)
    yesterday = datetime.now(tz).date() - timedelta(days=1)
    return dt.astimezone(tz).date() == yesterday
