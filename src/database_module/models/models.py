"""
This module defines the updated SQLAlchemy ORM models for the FastAPI application.
These models include user management, document storage, ticketing system, events, and authentication tokens.

Classes:
    Base: The base class for all ORM models.
    UserRole: Represents roles assigned to users.
    User: Represents system users and their related data.
    CheckCode: Represents codes used for verification purposes during registration or login.
    Ticket: Represents tickets related to document processing, their statuses, events, and other metadata.
    TicketType: Represents different types of tickets.
    TicketStatus: Represents different statuses for tickets.
    Document: Represents user-uploaded documents and their association with users and tickets.
    DocumentSummary: Represents a summary of a document processed in the system.
    DocumentReport: Represents a report generated from document processing.
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
from src.database_module.utils.moscow_datetime import datetime_now_moscow


class Base(AsyncAttrs, DeclarativeBase):
    """
    The base class for all ORM models.
    This class is inherited by all the database models to provide basic functionality such as
    creating tables and associating them with the SQLAlchemy ORM.
    """
    __mapper_args__ = {'eager_defaults': True}


class UserRole(Base, AsyncAttrs):
    """
    Represents roles assigned to users.
    This model is used to define different roles that a user can have in the system,
    such as admin, user, etc.
    """
    __tablename__ = 'user_roles'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    users: Mapped[List["User"]] = relationship('User', back_populates='role', lazy='selectin')


class User(Base, AsyncAttrs):
    """
    Represents system users and their related data.
    This model holds information about the users, including their login credentials,
    personal details, role assignments, and the relationships with other entities
    like documents, tickets, and events.
    """
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    surname: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    organization: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('user_roles.id'), nullable=False)
    role: Mapped["UserRole"] = relationship('UserRole', lazy='selectin')

    check_codes: Mapped[List["CheckCode"]] = relationship(
        'CheckCode', back_populates='user', lazy='selectin')
    documents: Mapped[List["Document"]] = relationship(
        'Document', back_populates='user', lazy='selectin')
    tickets: Mapped[List["Ticket"]] = relationship('Ticket', back_populates='user', lazy='selectin')
    custom_events: Mapped[List["CustomEvent"]] = relationship(
        'CustomEvent', back_populates='user', lazy='selectin')
    tokens: Mapped[List["Token"]] = relationship('Token', back_populates='user', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True),
        default=datetime_now_moscow,
        onupdate=datetime_now_moscow)


class CheckCode(Base, AsyncAttrs):
    """
    Represents codes used for verification purposes during registration or login.
    This model stores verification codes sent to users for account verification or password reset.
    """
    __tablename__ = 'check_codes'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(6), nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship('User', back_populates='check_codes', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)


class Ticket(Base, AsyncAttrs):
    """
    Represents tickets related to document processing, their statuses, events, and other metadata.
    This model links user-uploaded documents with ticket statuses, events, and processing stages.
    """
    __tablename__ = 'tickets'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shared: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship('User', back_populates='tickets', lazy='selectin')
    ticket_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey('ticket_types.id'), nullable=True)
    ticket_type: Mapped["TicketType"] = relationship(
        'TicketType', back_populates='tickets', lazy='selectin')
    ticket_status_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('ticket_statuses.id'), nullable=False)
    ticket_status: Mapped["TicketStatus"] = relationship(
        'TicketStatus', back_populates='tickets', lazy='selectin')
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey('events.id'), nullable=True)
    event: Mapped["Event"] = relationship(
        'Event', back_populates='tickets', lazy='selectin')
    custom_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey('custom_events.id'), nullable=True)
    custom_event: Mapped["CustomEvent"] = relationship(
        'CustomEvent', back_populates='tickets', lazy='selectin')

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('documents.id'), nullable=False, unique=True)
    document: Mapped["Document"] = relationship(
        'Document', back_populates='ticket', lazy='selectin')
    document_summary_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey('document_summaries.id'), nullable=True, unique=True)
    document_summary: Mapped["DocumentSummary"] = relationship(
        'DocumentSummary', back_populates='ticket', lazy='selectin')
    document_report_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey('document_reports.id'), nullable=True, unique=True)
    document_report: Mapped["DocumentReport"] = relationship(
        'DocumentReport', back_populates='ticket', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)


class TicketType(Base, AsyncAttrs):
    """
    Represents different types of tickets.
    This model is used to track the various types of a tickets.
    """
    __tablename__ = 'ticket_types'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    tickets: Mapped[List["Ticket"]] = relationship(
        'Ticket', back_populates='ticket_type', lazy='selectin')


class TicketStatus(Base, AsyncAttrs):
    """
    Represents different statuses for tickets.
    This model is used to track the various stages of a ticket during its lifecycle, such as "open", "in progress", or "closed".
    """
    __tablename__ = 'ticket_statuses'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    tickets: Mapped[List["Ticket"]] = relationship(
        'Ticket', back_populates='ticket_status', lazy='selectin')


class Document(Base, AsyncAttrs):
    """
    Represents user-uploaded documents and their association with users and tickets.
    This model stores information about the documents uploaded by users, including the file path and user associations.
    """
    __tablename__ = 'documents'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship('User', back_populates='documents', lazy='selectin')

    ticket: Mapped["Ticket"] = relationship(
        'Ticket',
        back_populates='document',
        uselist=False,
        lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)


class DocumentSummary(Base, AsyncAttrs):
    """
    Represents a summary of a document processed in the system.
    This model is used to store summaries of processed documents, typically after a document has been analyzed or reviewed.
    """
    __tablename__ = 'document_summaries'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)

    ticket: Mapped["Ticket"] = relationship(
        'Ticket',
        back_populates='document_summary',
        uselist=False,
        lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)


class DocumentReport(Base, AsyncAttrs):
    """
    Represents a report generated from document processing.
    This model stores reports related to documents processed in the system, which could include analysis results or processing outcomes.
    """
    __tablename__ = 'document_reports'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)

    ticket: Mapped["Ticket"] = relationship(
        'Ticket',
        back_populates='document_report',
        uselist=False,
        lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)


class Token(Base, AsyncAttrs):
    """
    Stores authentication tokens for user sessions.
    This model stores tokens used for user authentication, such as refresh tokens for maintaining user sessions.
    """
    __tablename__ = 'tokens'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    checker: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship('User', back_populates='tokens', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)


class Event(Base, AsyncAttrs):
    """
    Represents predefined events in the system.
    This model is used to define predefined events that can trigger tickets or other system actions.
    """
    __tablename__ = 'events'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tickets: Mapped[List["Ticket"]] = relationship(
        'Ticket', back_populates='event', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)


class CustomEvent(Base, AsyncAttrs):
    """
    Represents user-defined custom events.
    This model allows users to create custom events, which can be linked to tickets for tracking or processing purposes.
    """
    __tablename__ = 'custom_events'
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uix_custom_events_user_id_name'),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship('User', back_populates='custom_events', lazy='selectin')

    tickets: Mapped[List["Ticket"]] = relationship(
        'Ticket', back_populates='custom_event', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)
