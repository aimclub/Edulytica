import uuid
from typing import List, Optional
from sqlalchemy import String, DateTime, Boolean, Text, ForeignKey
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
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('user_roles.id'), nullable=False)
    role: Mapped["UserRole"] = relationship('UserRole', lazy='selectin')

    documents: Mapped[List["Document"]] = relationship('Document', back_populates='user', lazy='selectin')
    tickets: Mapped[List["Ticket"]] = relationship('Ticket', back_populates='user', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow, onupdate=datetime_now_moscow)


class Document(Base, AsyncAttrs):
    __tablename__ = 'documents'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship('User', back_populates='documents', lazy='selectin')

    tickets: Mapped[List["Ticket"]] = relationship('Ticket', back_populates='document', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)


class Ticket(Base, AsyncAttrs):
    __tablename__ = 'tickets'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship('User', back_populates='tickets', lazy='selectin')
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('documents.id'), nullable=False)
    document: Mapped["Document"] = relationship('Document', back_populates='tickets', lazy='selectin')
    model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('models.id'), nullable=False)
    model: Mapped["Model"] = relationship('Model', back_populates='tickets', lazy='selectin')
    ticket_status_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('ticket_statuses.id'), nullable=False)
    ticket_status: Mapped["TicketStatus"] = relationship('TicketStatus', lazy='selectin')

    comments: Mapped[List["Comment"]] = relationship('Comment', back_populates='ticket', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)


class TicketStatus(Base, AsyncAttrs):
    __tablename__ = 'ticket_statuses'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class Model(Base, AsyncAttrs):
    __tablename__ = 'models'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tickets: Mapped[List["Ticket"]] = relationship('Ticket', back_populates='model', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)


class Comment(Base, AsyncAttrs):
    __tablename__ = 'comments'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    ticket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('tickets.id'), nullable=False)
    ticket: Mapped["Ticket"] = relationship('Ticket', back_populates='comments', lazy='selectin')
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship('User', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)


class DocumentReport(Base, AsyncAttrs):
    __tablename__ = 'document_reports'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)

    ticket_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('tickets.id'), nullable=False)
    ticket: Mapped["Ticket"] = relationship('Ticket', back_populates='reports', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)


class Token(Base, AsyncAttrs):
    __tablename__ = 'tokens'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship('User', back_populates='tokens', lazy='selectin')

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime_now_moscow)
