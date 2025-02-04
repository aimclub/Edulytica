from datetime import datetime, timezone, timedelta


def datetime_now_moscow():
    return datetime.now(timezone(timedelta(hours=3)))
