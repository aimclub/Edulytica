from datetime import datetime
from typing import Optional
from pydantic import BaseModel, UUID4, ConfigDict


class _UserCrop(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    username: str
    email: str
    password: str
    disabled: bool
    created_at: datetime
    updated_at: datetime


class _TokenCrop(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user_id: UUID4
    refresh_token: str
    checker: UUID4
    status: Optional[bool] = None
    created_at: datetime


class _FileStatusCrop(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: Optional[str] = None


class _FilesCrop(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file: Optional[str] = None
    data_create: datetime
    status_id: int


class _ResultFilesCrop(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    file: str
    data_create: datetime
    user_id: UUID4
    ticket_id: UUID4


class _TicketsCrop(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    ticket_type: Optional[str] = None
    created_date: datetime
    user_id: UUID4
    status_id: int


class _TicketStatusesCrop(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: Optional[str] = None
