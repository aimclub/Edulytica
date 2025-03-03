"""
This module provides a utility function for obtaining the current datetime in the Moscow timezone.
"""

from datetime import datetime, timezone, timedelta


def datetime_now_moscow():
    """
    Returns the current datetime in the Moscow timezone (UTC+3).

    Returns:
        datetime: The current datetime with the UTC+3 timezone.
    """
    return datetime.now(timezone(timedelta(hours=3)))
