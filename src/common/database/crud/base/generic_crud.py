"""
This module provides a generic CRUD base for working with SQLAlchemy ORM models asynchronously.
It simplifies common database operations by providing reusable methods for
fetching, creating, updating, and deleting records.
"""

from __future__ import annotations
from typing import ClassVar, Generic, Optional, Type, TypeVar, List, Any
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import select, update as sa_update, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


ModelT = TypeVar("ModelT", bound=DeclarativeBase)
GetSchemaT = TypeVar("GetSchemaT", bound=BaseModel)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)


class GenericCrud(Generic[ModelT, GetSchemaT, CreateSchemaT, UpdateSchemaT]):
    """
    A generic CRUD base that provides common database operations for a given SQLAlchemy model.

    Attributes:
        base_model (ModelT): The SQLAlchemy model associated with this CRUD.
        update_schema (Type[UpdateSchemaT]): The Pydantic schema used for updating records.
        create_schema (Type[CreateSchemaT]): The Pydantic schema used for creating new records.
        get_schema (Type[GetSchemaT]): The Pydantic schema used for retrieving records.
    """

    base_model: ClassVar[Type[ModelT]]
    update_schema: ClassVar[Type[UpdateSchemaT]]
    create_schema: ClassVar[Type[CreateSchemaT]]
    get_schema: ClassVar[Type[GetSchemaT]]

    @classmethod
    async def get_by_id(cls, session: AsyncSession, record_id: UUID) -> Optional[GetSchemaT]:
        """
        Retrieves a record by its ID.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            record_id (UUID): The unique identifier of the record.

        Returns:
            Optional[GetSchemaT]: The retrieved record as a Pydantic model or None if not found.
        """
        res = await session.execute(select(cls.base_model).where(cls.base_model.id == record_id))
        obj = res.scalar_one_or_none()
        return cls.get_schema.model_validate(obj) if obj else None

    @classmethod
    async def get_by_id_no_validate(cls, session: AsyncSession, record_id: UUID) -> Optional[ModelT]:
        """
        Retrieves a record by its ID without applying Pydantic validation.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            record_id (UUID): The unique identifier of the record.

        Returns:
            Optional[ModelT]: The retrieved ORM record or None if not found.
        """
        res = await session.execute(select(cls.base_model).where(cls.base_model.id == record_id))
        return res.scalar_one_or_none()

    @classmethod
    async def get_all(cls, session: AsyncSession, offset: int = 0, limit: int = 100) -> List[GetSchemaT]:
        """
        Retrieves all records with pagination support.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            offset (int): The starting index of records.
            limit (int): The maximum number of records to retrieve.

        Returns:
            List[GetSchemaT]: A list of retrieved records as Pydantic models.
        """
        res = await session.execute(select(cls.base_model).offset(offset).limit(limit))
        return [cls.get_schema.model_validate(x) for x in res.scalars().all()]

    @classmethod
    async def get_filtered_by_params(cls, session: AsyncSession, **kwargs) -> List[GetSchemaT]:
        """
        Retrieves records filtered by keyword arguments.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            **kwargs: Filter parameters.

        Returns:
            List[GetSchemaT]: A list of filtered records as Pydantic models.
        """
        res = await session.execute(select(cls.base_model).filter_by(**kwargs))
        return [cls.get_schema.model_validate(x) for x in res.scalars().all()]

    @classmethod
    async def get_filtered(cls, session: AsyncSession, filter_) -> List[GetSchemaT]:
        """
        Retrieves records using a custom filter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            filter_: SQLAlchemy filter expression.

        Returns:
            List[GetSchemaT]: A list of filtered records as Pydantic models.
        """
        res = await session.execute(select(cls.base_model).filter(filter_))
        return [cls.get_schema.model_validate(x) for x in res.scalars().all()]

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> GetSchemaT:
        """
        Creates a new record in the database.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            **kwargs: Record data.

        Returns:
            GetSchemaT: The created record as a Pydantic model.
        """
        instance = cls.base_model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return cls.get_schema.model_validate(instance)

    @classmethod
    async def update(cls, session: AsyncSession, record_id: UUID, **kwargs) -> Optional[GetSchemaT]:
        """
        Updates an existing record.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            record_id (UUID): The unique identifier of the record.
            **kwargs: Fields to update.

        Returns:
            Optional[GetSchemaT]: The updated record as a Pydantic model or None if not found.
        """
        clean_kwargs = {key: value for key, value in kwargs.items() if value is not None}
        await session.execute(
            sa_update(cls.base_model).where(cls.base_model.id == record_id).values(**clean_kwargs)
        )
        await session.commit()
        return await cls.get_by_id(session, record_id)

    @classmethod
    async def delete(cls, session: AsyncSession, record_id: UUID) -> None:
        """
        Deletes a record by its ID.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            record_id (UUID): The unique identifier of the record.
        """
        await session.execute(sa_delete(cls.base_model).where(cls.base_model.id == record_id))
        await session.commit()
