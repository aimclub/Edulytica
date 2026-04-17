from .account import account_v1
from .feedback import feedback_v1
from .internal import internal_v1
from .events import events_v1
from .tickets import tickets_v1
from .files import files_v1


routers = [
    account_v1,
    feedback_v1,
    internal_v1,
    events_v1,
    tickets_v1,
    files_v1
]


__all__ = [
    "account_v1", "feedback_v1", "internal_v1",
    "events_v1", "tickets_v1", "files_v1", "routers"
]
