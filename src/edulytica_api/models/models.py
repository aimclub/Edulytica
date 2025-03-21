"""
This module defines the SQLAlchemy ORM models for the FastAPI application.
It includes models for users, authentication tokens, file management, and ticketing system.

Classes:
    Base: The base class for all ORM models.
    User: Represents a user in the system.
    Token: Stores refresh tokens for authentication.
    FileStatus: Represents the status of files.
    Files: Stores file-related data.
    ResultFiles: Stores processed files related to tickets and users.
    Tickets: Represents support or processing tickets.
    TicketStatuses: Represents different statuses of tickets.
"""

import uuid
import datetime
from sqlalchemy import DateTime, Boolean, UUID, Column, String, Integer, ForeignKey
from typing import List
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, relationship, mapped_column, DeclarativeBase
from src.edulytica_api.utils.moscow_datetime import datetime_now_moscow


class Base(AsyncAttrs, DeclarativeBase):
    __mapper_args__ = {'eager_defaults': True}


class User(Base, AsyncAttrs):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    username = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    disabled = Column(Boolean, nullable=False, default=False)

    result_files: Mapped[List["DocumentReport"]] = relationship(back_populates="user")
    ticket: Mapped[List["Tickets"]] = relationship(back_populates="user")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True),
        default=datetime_now_moscow,
        onupdate=datetime_now_moscow)


class Token(Base, AsyncAttrs):
    __tablename__ = "tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    refresh_token = Column(String(450), nullable=False)
    checker = Column(UUID, nullable=False)
    status = Column(Boolean)

    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime_now_moscow)


class FileStatus(Base, AsyncAttrs):
    __tablename__ = "file_statuses"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    files: Mapped[List["Files"]] = relationship(back_populates="status")


class Files(Base, AsyncAttrs):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    file = Column(String)
    data_create = Column(DateTime(timezone=True), default=datetime_now_moscow)
    status_id: Mapped[int] = mapped_column(ForeignKey("file_statuses.id"))
    status: Mapped["FileStatus"] = relationship(back_populates="files")


class DocumentReport(Base, AsyncAttrs):
    __tablename__ = "result_files"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4, index=True)
    file = Column(String)
    data_create = Column(DateTime(timezone=True), default=datetime_now_moscow)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="result_files")
    ticket_id: Mapped[UUID] = mapped_column(ForeignKey("tickets.id"))
    ticket: Mapped["Tickets"] = relationship(back_populates="result_files")


class Tickets(Base, AsyncAttrs):
    __tablename__ = "tickets"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4, index=True)
    ticket_type = Column(String)
    created_date = Column(DateTime(timezone=True), default=datetime_now_moscow)
    result_files: Mapped[List["DocumentReport"]] = relationship(back_populates="ticket")
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="ticket")
    status_id: Mapped[Integer] = mapped_column(ForeignKey("ticket_statuses.id"))
    status: Mapped["TicketStatuses"] = relationship(back_populates="ticket")


class TicketStatuses(Base, AsyncAttrs):
    __tablename__ = "ticket_statuses"
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    status = Column(String)
    ticket: Mapped[List["Tickets"]] = relationship(back_populates="status")
