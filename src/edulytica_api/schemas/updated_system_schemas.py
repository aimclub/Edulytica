from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, UUID4


class _UserRoleCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class _UserRoleUpdate(_UserRoleCreate):
    id: UUID4


class _UserRoleGet(_UserRoleUpdate):
    pass


class _UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    login: str
    email: str
    password_hash: str
    name: Optional[str] = None
    surname: Optional[str] = None
    organization: Optional[str] = None
    role_id: UUID4


class _UserUpdate(_UserCreate):
    id: UUID4
    is_active: bool


class _UserGet(_UserUpdate):
    created_at: datetime
    updated_at: datetime


class _CheckCodeCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    user_id: UUID4


class _CheckCodeUpdate(_CheckCodeCreate):
    id: UUID4


class _CheckCodeGet(_CheckCodeUpdate):
    created_at: datetime


class _TicketCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prompt: Optional[str] = None
    shared: Optional[bool] = False
    user_id: UUID4
    ticket_status_id: UUID4
    event_id: Optional[UUID4] = None
    custom_event_id: Optional[UUID4] = None
    document_id: UUID4
    document_summary_id: Optional[UUID4] = None
    document_report_id: Optional[UUID4] = None


class _TicketUpdate(_TicketCreate):
    id: UUID4


class _TicketGet(_TicketUpdate):
    created_at: datetime


class _TicketStatusCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class _TicketStatusUpdate(_TicketStatusCreate):
    id: UUID4


class _TicketStatusGet(_TicketStatusUpdate):
    pass


class _DocumentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID4]
    file_path: str
    user_id: UUID4


class _DocumentUpdate(_DocumentCreate):
    pass


class _DocumentGet(_DocumentUpdate):
    created_at: datetime


class _DocumentSummaryCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID4]
    file_path: str


class _DocumentSummaryUpdate(_DocumentSummaryCreate):
    pass


class _DocumentSummaryGet(_DocumentSummaryUpdate):
    created_at: datetime


class _DocumentReportCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID4]
    file_path: str


class _DocumentReportUpdate(_DocumentReportCreate):
    pass


class _DocumentReportGet(_DocumentReportUpdate):
    created_at: datetime


class _TokenCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    refresh_token: str
    user_id: UUID4


class _TokenUpdate(_TokenCreate):
    id: UUID4


class _TokenGet(_TokenUpdate):
    created_at: datetime


class _EventCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: Optional[str] = None


class _EventUpdate(_EventCreate):
    id: UUID4


class _EventGet(_EventUpdate):
    created_at: datetime


class _CustomEventCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: Optional[str] = None
    user_id: UUID4


class _CustomEventUpdate(_CustomEventCreate):
    id: UUID4


class _CustomEventGet(_CustomEventUpdate):
    created_at: datetime
