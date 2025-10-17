import asyncio
from logging.config import fileConfig
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from src.common.database.models import Base
from src.common.config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_IP, POSTGRES_PORT, POSTGRES_DB


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

DATABASE_URL = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_IP}:{POSTGRES_PORT}/{POSTGRES_DB}'

target_metadata = Base.metadata

async_engine = create_async_engine(DATABASE_URL, future=True)


async def run_migrations_online():
    async with async_engine.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection: AsyncConnection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(url=DATABASE_URL, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(run_migrations_online())
