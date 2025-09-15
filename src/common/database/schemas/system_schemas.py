from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class UserRoleCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class UserRoleUpdate(UserRoleCreate):
    id: UUID


class UserRoleGet(UserRoleUpdate):
    pass


class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    login: str
    email: str
    password_hash: str
    name: Optional[str] = None
    surname: Optional[str] = None
    organization: Optional[str] = None
    role_id: UUID


class UserUpdate(UserCreate):
    id: UUID
    is_active: bool


class UserGet(UserUpdate):
    created_at: datetime
    updated_at: datetime


class CheckCodeCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    user_id: UUID


class CheckCodeUpdate(CheckCodeCreate):
    id: UUID


class CheckCodeGet(CheckCodeUpdate):
    created_at: datetime


class TicketCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    shared: Optional[bool] = False
    name: Optional[str] = ""
    user_id: UUID
    ticket_type_id: Optional[UUID] = None
    ticket_status_id: UUID
    event_id: Optional[UUID] = None
    custom_event_id: Optional[UUID] = None
    document_id: UUID
    document_summary_id: Optional[UUID] = None
    document_report_id: Optional[UUID] = None


class TicketUpdate(TicketCreate):
    id: UUID


class TicketGet(TicketUpdate):
    created_at: datetime


class TicketStatusCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class TicketStatusUpdate(TicketStatusCreate):
    id: UUID


class TicketStatusGet(TicketStatusUpdate):
    pass


class TicketTypeCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class TicketTypeUpdate(TicketTypeCreate):
    id: UUID


class TicketTypeGet(TicketTypeUpdate):
    pass


class DocumentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID]
    file_path: str
    user_id: UUID


class DocumentUpdate(DocumentCreate):
    pass


class DocumentGet(DocumentUpdate):
    created_at: datetime


class DocumentSummaryCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID]
    file_path: str


class DocumentSummaryUpdate(DocumentSummaryCreate):
    pass


class DocumentSummaryGet(DocumentSummaryUpdate):
    created_at: datetime


class DocumentReportCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID]
    file_path: str


class DocumentReportUpdate(DocumentReportCreate):
    pass


class DocumentReportGet(DocumentReportUpdate):
    created_at: datetime


class TokenCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    refresh_token: str
    checker: UUID
    user_id: UUID


class TokenUpdate(TokenCreate):
    id: UUID


class TokenGet(TokenUpdate):
    created_at: datetime


class EventCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: Optional[str] = None


class EventUpdate(EventCreate):
    id: UUID


class EventGet(EventUpdate):
    created_at: datetime


class CustomEventCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: Optional[str] = None
    user_id: UUID


class CustomEventUpdate(CustomEventCreate):
    id: UUID


class CustomEventGet(CustomEventUpdate):
    created_at: datetime
