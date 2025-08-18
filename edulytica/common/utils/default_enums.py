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
