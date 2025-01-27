import uuid
from sqlalchemy import DateTime, Boolean, UUID, text, TIMESTAMP, Column, String, Integer
import datetime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


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
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))


class Token(Base, AsyncAttrs):
    __tablename__ = "tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    refresh_token = Column(String(450), nullable=False)
    checker = Column(UUID, nullable=False)
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)


class FileStatus(Base, AsyncAttrs):
    __tablename__ = "file_statuses"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)


class Files(Base, AsyncAttrs):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    file = Column(String)
    data_create = Column(DateTime, default=datetime.datetime.now)


class ResultFiles(Base, AsyncAttrs):
    __tablename__ = "result_files"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4, index=True)
    file = Column(String)
    data_create = Column(DateTime, default=datetime.datetime.now)


class Tickets(Base, AsyncAttrs):
    __tablename__ = "tickets"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4, index=True)
    ticket_type = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.now)


class TicketStatuses(Base, AsyncAttrs):
    __tablename__ = "ticket_statuses"
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    status = Column(String)
