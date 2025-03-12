"""
This module sets up the asynchronous database connection using SQLAlchemy and provides session management for FastAPI.
"""

import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine


load_dotenv()
DATABASE_URL = f'postgresql+asyncpg://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_IP")}:{os.environ.get("POSTGRES_PORT")}/{os.environ.get("POSTGRES_DB")}'
engine = create_async_engine(DATABASE_URL, future=True)
SessionLocal = async_sessionmaker(
bind=engine, expire_on_commit=False, autocommit=False, autoflush=False, class_=AsyncSession, future=True)


async def get_session() -> Generator:
    """
    Provides an async database session for FastAPI routes.

    Yields:
        AsyncSession: The database session instance.
    """
    session: AsyncSession = SessionLocal()
    try:
        yield session
    finally:
        await session.close()
