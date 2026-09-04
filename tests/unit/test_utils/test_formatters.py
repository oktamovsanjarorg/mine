from src.core.utils.formatters import format_number, format_currency, format_file_size, format_duration, progress_bar


def test_format_number():
    assert format_number(1234567) == "1 234 567"
    assert format_number(0) == "0"


def test_format_currency():
    assert format_currency(1500000) == "1 500 000 UZS"


def test_format_file_size():
    assert format_file_size(1024) == "1 KB"
    assert format_file_size(1048576) == "1 MB"
    assert format_file_size(0) == "0 B"


def test_format_duration():
    assert format_duration(90) == "1 soat 30 min"
    assert format_duration(60) == "1 soat"
    assert format_duration(45) == "45 min"


def test_progress_bar():
    bar = progress_bar(5, 10, length=10)
    assert bar == "█████░░░░░ 50%"
