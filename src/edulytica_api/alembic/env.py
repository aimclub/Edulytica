import asyncio
import os
from logging.config import fileConfig
from alembic import context
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection

from src.edulytica_api.models.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

load_dotenv()
DATABASE_URL = f'postgresql+asyncpg://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_IP")}:{os.environ.get("POSTGRES_PORT")}/{os.environ.get("POSTGRES_DB")}'

target_metadata = Base.metadata

async_engine = create_async_engine(DATABASE_URL, future=True)


async def run_migrations_online():
    async with async_engine.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection: AsyncConnection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(url=DATABASE_URL, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(run_migrations_online())
