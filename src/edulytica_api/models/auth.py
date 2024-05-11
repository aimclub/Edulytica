import uuid

from sqlalchemy import Column, Integer, String, DateTime, Boolean, UUID, text, TIMESTAMP
import datetime
from src.edulytica_api.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    username = Column(String(50),  nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    disabled = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))

class Token(Base):
    __tablename__ = "tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    refresh_token = Column(String(450), nullable=False)
    checker = Column(UUID, nullable=False)
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)