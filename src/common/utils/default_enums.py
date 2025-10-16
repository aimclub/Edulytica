from enum import Enum


class UserRoleDefault(str, Enum):
    USER = 'User'


class TicketStatusDefault(str, Enum):
    CREATED = 'Created'
    IN_PROGRESS = 'In progress'
    COMPLETED = 'Completed'
    FAILED = 'Failed'


class TicketTypeDefault(str, Enum):
    ACHIEVABILITY = 'Достижимость'


class SubtaskStatuses(str, Enum):
    STATUS_PENDING = "PENDING"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"
