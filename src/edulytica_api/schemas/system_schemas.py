from datetime import datetime
from pydantic import BaseModel, ConfigDict, UUID4


class _UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: str
    password: str


class _UserUpdate(_UserCreate):
    id: UUID4


class _UserGet(_UserUpdate):
    disabled: bool

    created_at: datetime
    updated_at: datetime


class _TokenCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID4
    refresh_token: str
    checker: UUID4
    status: bool


class _TokenUpdate(_TokenCreate):
    id: UUID4


class _TokenGet(_TokenUpdate):
    created_date: datetime


class _ResultFilesCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    file: str
    user_id: UUID4
    ticket_id: UUID4


class _ResultFilesUpdate(_ResultFilesCreate):
    id: UUID4


class _ResultFilesGet(_ResultFilesUpdate):
    data_create: datetime


class _TicketsCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_type: str
    user_id: UUID4
    status_id: int


class _TicketsUpdate(_TicketsCreate):
    id: UUID4


class _TicketsGet(_TicketsUpdate):
    created_date: datetime
