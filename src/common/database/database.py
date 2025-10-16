"""
This module sets up the asynchronous database connection using SQLAlchemy and provides session management for FastAPI.
"""

from typing import Generator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from src.common.config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_IP, POSTGRES_PORT, POSTGRES_DB


load_dotenv()
DATABASE_URL = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_IP}:{POSTGRES_PORT}/{POSTGRES_DB}'
engine = create_async_engine(DATABASE_URL, future=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autocommit=False,
                                  autoflush=False, class_=AsyncSession, future=True)


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
