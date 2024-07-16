import uuid
from sqlalchemy import DateTime, Boolean, UUID, text, TIMESTAMP, Column, String, Integer, ForeignKey
import datetime
from typing import List
from sqlalchemy.orm import Mapped, relationship, mapped_column
from src.edulytica_api.database import Base


class User(Base):
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

    result_files: Mapped[List["ResultFiles"]] = relationship(back_populates="user")
    ticket: Mapped[List["Tickets"]] = relationship(back_populates="user")


class Token(Base):
    __tablename__ = "tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    refresh_token = Column(String(450), nullable=False)
    checker = Column(UUID, nullable=False)
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)


class FileStatus(Base):
    __tablename__ = "file_statuses"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    files: Mapped[List["Files"]] = relationship(back_populates="status")


class Files(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    file = Column(String)
    data_create = Column(DateTime, default=datetime.datetime.now)
    status_id: Mapped[int] = mapped_column(ForeignKey("file_statuses.id"))
    status: Mapped["FileStatus"] = relationship(back_populates="files")


class ResultFiles(Base):
    __tablename__ = "result_files"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4, index=True)
    file = Column(String)
    data_create = Column(DateTime, default=datetime.datetime.now)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="result_files")
    ticket_id: Mapped[UUID] = mapped_column(ForeignKey("tickets.id"))
    ticket: Mapped["Tickets"] = relationship(back_populates="result_files")


class Tickets(Base):
    __tablename__ = "tickets"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4, index=True)
    ticket_type = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.now)
    result_files: Mapped[List["ResultFiles"]] = relationship(back_populates="ticket")
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="ticket")
    status_id: Mapped[Integer] = mapped_column(ForeignKey("ticket_statuses.id"))
    status: Mapped["TicketStatuses"] = relationship(back_populates="ticket")

class TicketStatuses(Base):
    __tablename__ = "ticket_statuses"
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    status = Column(String)
    ticket: Mapped[List["Tickets"]] = relationship(back_populates="status")
