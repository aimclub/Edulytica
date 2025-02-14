import logging
import inspect
from functools import wraps
from colorlog import ColoredFormatter
from src.edulytica_api.utils.moscow_datetime import datetime_now_moscow


class CustomColoredFormatter(ColoredFormatter):
    def format(self, record):
        levelname = record.levelname
        if record.levelname == "DEBUG":
            return f"\033[37m{levelname:<8} {record.getMessage()}\033[0m"
        else:
            formatted_message = super().format(record)
            return formatted_message.replace(f"{levelname}:",
                                             f"{levelname:<8}")


handler = logging.StreamHandler()
formatter = CustomColoredFormatter(
    "%(log_color)s%(levelname)s:%(reset)s %(message)s",
    log_colors={
        "DEBUG": "white",
        "INFO": "cyan",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def _sub_api_logs(handler):
    @wraps(handler)
    async def wrapper(*args, **kwargs):
        bound_arguments = inspect.signature(handler).bind(*args, **kwargs).arguments
        params = {key: value for key, value in bound_arguments.items() if key not in ('session', 'auth_data')}

        log_text = ''
        if 'auth_data' in bound_arguments:
            user = bound_arguments['auth_data']['user']
            log_text += f'User: ID({user.id})\n'

        log_text += f'Handler: {handler.__name__} | Params: {params}'

        try:
            logger.debug('----------------------------')
            logger.debug(f'TIME: {datetime_now_moscow()}')
            logger.info(log_text)
            return await handler(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            raise

    return wrapper


def api_logs(route_decorator):
    def wrapper(handler):
        wrapped_handler = _sub_api_logs(handler)
        return route_decorator(wrapped_handler)
    return wrapper




