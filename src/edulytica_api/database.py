import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
load_dotenv()
DATABASE_URL = f"postgresql://{os.environ.get("POSTGRES_LOGIN")}:{os.environ.get("POSTGRES_PASS")}@{os.environ.get("POSTGRES_IP")}:{os.environ.get("POSTGRES_PORT")}/{os.environ.get("POSTGRES_DB")}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# engine = create_async_engine(
#     DATABASE_URL,
#     echo=True,
# )
#
# sessionmaker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
#
#
# async def get_session() -> AsyncGenerator[AsyncSession, None]:
#     async with sessionmaker() as session:
#         yield session