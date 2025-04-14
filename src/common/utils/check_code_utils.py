from datetime import datetime, timedelta
from random import randint
from src.common.utils.moscow_datetime import datetime_now_moscow, set_moscow_timezone


def generate_code():
    return str(randint(1000000, 9999999))[1:]


def check_expired_code(created_date: datetime):
    return (set_moscow_timezone(created_date) < datetime_now_moscow()
            - timedelta(seconds=60))
