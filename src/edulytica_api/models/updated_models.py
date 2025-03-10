"""
This module defines the updated SQLAlchemy ORM models for the FastAPI application.
These models include user management, document storage, ticketing system, events, and authentication tokens.

Classes:
    Base: The base class for all ORM models.
    UserRole: Represents roles assigned to users.
    User: Represents system users.
    Document: Represents user-uploaded documents.
    Ticket: Represents tickets related to document processing.
    TicketStatus: Represents different statuses for tickets.
    Comment: Represents user comments on tickets.
    DocumentReport: Represents reports generated from document processing.
    Token: Stores authentication tokens for user sessions.
    Event: Represents predefined events in the system.
    CustomEvent: Represents user-defined custom events.
"""

import uuid
from typing import List, Optional
from sqlalchemy import String, DateTime, Boolean, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from src.edulytica_api.utils.moscow_datetime import datetime_now_moscow


class Base(AsyncAttrs, DeclarativeBase):
    __mapper_args__ = {'eager_defaults': True}


class UserRole(Base, AsyncAttrs):
    __tablename__ = 'user_roles'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class User(Base, AsyncAttrs):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    surname: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    organization: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('user_roles.id'), nullable=False)
    role: Mapped["UserRole"] = relationship('UserRole', lazy='selectin')

    sent_code: Mapped["SentCode"] = relationship('SentCode', back_populates='user', lazy='selectin')
    documents: Mapped[List["Document"]] = relationship('Document', back_populates='user', lazy='selectin')
    tickets: Mapped[List["Ticket"]] = relationship('Ticket', back_populates='user', lazy='selectin')
    custom_events: Mapped[List["CustomEvent"]] = relationship('CustomEvent', back_populates='user', lazy='selectin')
    tokens: Mapped[List["Token"]] = relationship('Token', back_populates='user', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow,
                                                 onupdate=datetime_now_moscow)


class SentCode(Base, AsyncAttrs):
    __tablename__ = 'sent_codes'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(6), nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user: Mapped["User"] = relationship('User', back_populates='sent_code', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)


class Ticket(Base, AsyncAttrs):
    __tablename__ = 'tickets'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    shared: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship('User', back_populates='tickets', lazy='selectin')
    ticket_status_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('ticket_statuses.id'),
                                                        nullable=False)
    ticket_status: Mapped["TicketStatus"] = relationship('TicketStatus', lazy='selectin')
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey('events.id'), nullable=True)
    event: Mapped["Event"] = relationship('Event', back_populates='tickets', lazy='selectin')
    custom_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey('custom_events.id'), nullable=True)
    custom_event: Mapped["CustomEvent"] = relationship('CustomEvent', back_populates='tickets', lazy='selectin')

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('documents.id'), nullable=False, unique=True)
    document: Mapped["Document"] = relationship('Document', back_populates='ticket', lazy='selectin')
    document_summary_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey('document_summaries.id'), nullable=True, unique=True)
    document_summary: Mapped["DocumentSummary"] = relationship('DocumentSummary', back_populates='ticket',
                                                               lazy='selectin')
    document_report_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey('document_reports.id'), nullable=True, unique=True)
    document_report: Mapped["DocumentReport"] = relationship('DocumentReport', back_populates='ticket', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)


class TicketStatus(Base, AsyncAttrs):
    __tablename__ = 'ticket_statuses'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class Document(Base, AsyncAttrs):
    __tablename__ = 'documents'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship('User', back_populates='documents', lazy='selectin')

    ticket: Mapped["Ticket"] = relationship('Ticket', back_populates='document', uselist=False, lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)


class DocumentSummary(Base, AsyncAttrs):
    __tablename__ = 'document_summaries'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)

    ticket: Mapped["Ticket"] = relationship('Ticket', back_populates='document_summary', uselist=False, lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)


class DocumentReport(Base, AsyncAttrs):
    __tablename__ = 'document_reports'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)

    ticket: Mapped["Ticket"] = relationship('Ticket', back_populates='document_report', uselist=False, lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)


class Token(Base, AsyncAttrs):
    __tablename__ = 'tokens'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship('User', back_populates='tokens', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)


class Event(Base, AsyncAttrs):
    __tablename__ = 'events'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tickets: Mapped[List["Ticket"]] = relationship('Ticket', back_populates='event', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)


class CustomEvent(Base, AsyncAttrs):
    __tablename__ = 'custom_events'
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uix_custom_events_user_id_name'),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship('User', back_populates='custom_events', lazy='selectin')

    tickets: Mapped[List["Ticket"]] = relationship('Ticket', back_populates='custom_event', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)
