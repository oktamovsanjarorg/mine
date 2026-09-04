import pytest
from datetime import datetime, timedelta, timezone
from src.core.utils.datetime import parse_datetime, format_relative, is_today

def test_parse_datetime():
    dt = parse_datetime("30m")
    diff = dt - datetime.now(timezone.utc)
    assert 29 < diff.total_seconds() / 60 <= 30

    dt2 = parse_datetime("2h")
    diff2 = dt2 - datetime.now(timezone.utc)
    assert 1.9 < diff2.total_seconds() / 3600 <= 2.0

def test_format_relative():
    now = datetime.now(timezone.utc)
    assert format_relative(now - timedelta(minutes=5)) == "5 daqiqa oldin"
    assert format_relative(now + timedelta(hours=2)) == "2 soat keyin"

def test_is_today():
    now = datetime.now(timezone.utc)
    assert is_today(now) is True
    assert is_today(now - timedelta(days=1)) is False
