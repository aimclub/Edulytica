"""
This module provides a utility function for obtaining the datetime in the Moscow timezone.
"""

from datetime import datetime, timezone, timedelta


def set_moscow_timezone(dt: datetime) -> datetime:
    """
    Returns the datetime in the Moscow timezone (UTC+3).

    Returns:
        datetime: The datetime with the UTC+3 timezone.
    """
    moscow_tz = timezone(timedelta(hours=3))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=moscow_tz)
    else:
        return dt.astimezone(moscow_tz)


def datetime_now_moscow():
    """
    Returns the current datetime in the Moscow timezone (UTC+3).

    Returns:
        datetime: The current datetime with the UTC+3 timezone.
    """
    return datetime.now(timezone(timedelta(hours=3)))
