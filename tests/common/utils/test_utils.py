from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from src.common.utils.check_code_utils import generate_code
from src.common.utils.email import send_email
from src.common.utils.moscow_datetime import set_moscow_timezone, datetime_now_moscow


def test_generate_code():
    codes = []

    for _ in range(100):
        codes.append(generate_code())

    for code in codes:
        assert len(code) == 6
        assert isinstance(code, str)
        assert code.isdigit()
        assert 0 <= int(code) <= 999999


def test_set_moscow_timezone_naive_datetime():
    naive_dt = datetime(2024, 1, 1, 12, 0, 0)
    moscow_dt = set_moscow_timezone(naive_dt)

    assert moscow_dt.tzinfo is not None
    assert moscow_dt.tzinfo.utcoffset(moscow_dt) == timedelta(hours=3)
    assert moscow_dt.hour == 12


def test_set_moscow_timezone_aware_datetime():
    aware_dt = datetime(2024, 1, 1, 9, 0, 0, tzinfo=timezone.utc)
    moscow_dt = set_moscow_timezone(aware_dt)

    assert moscow_dt.tzinfo is not None
    assert moscow_dt.tzinfo.utcoffset(moscow_dt) == timedelta(hours=3)
    assert moscow_dt.hour == 12


def test_datetime_now_moscow():
    now_moscow = datetime_now_moscow()

    assert now_moscow.tzinfo is not None
    assert now_moscow.tzinfo.utcoffset(now_moscow) == timedelta(hours=3)

    utc_now = datetime.now(timezone.utc)
    utc_now_moscow = utc_now.astimezone(timezone(timedelta(hours=3)))

    delta_seconds = abs((now_moscow - utc_now_moscow).total_seconds())

    assert delta_seconds < 5


@patch('src.common.utils.email.smtplib.SMTP')
def test_send_email(mock_smtp):
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server

    to_email = "email@email.com"
    code = "123456"
    send_email(to_email, code)

    mock_smtp.assert_called_with('smtp.gmail.com', 587)

    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once()
    mock_server.sendmail.assert_called_once()
    mock_server.quit.assert_called_once()
