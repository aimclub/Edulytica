"""
This module provides a generic CRUD factory for working with SQLAlchemy ORM models asynchronously.
It simplifies common database operations by providing reusable methods for
 fetching, creating, updating, and deleting records.
"""

from typing import Type, TypeVar, List
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import update, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base

Schema = TypeVar("Schema", bound=BaseModel, covariant=True)
Model = TypeVar("Model", bound=declarative_base())


class CrudFactory:
    """
    A generic CRUD factory that provides common database operations for a given SQLAlchemy model.

    Attributes:
        base_model (Model): The SQLAlchemy model associated with this factory.
        update_schema (Type[Schema]): The Pydantic schema used for updating records.
        create_schema (Type[Schema]): The Pydantic schema used for creating new records.
        get_schema (Type[Schema]): The Pydantic schema used for retrieving records.
    """

    base_model: Model
    update_schema: Type[Schema]
    create_schema: Type[Schema]
    get_schema: Type[Schema]

    def __init__(
        self, base_model: Model, update_schema: Type[Schema], create_schema: Type[Schema], get_schema: Type[Schema]
    ):
        self.base_model = base_model
        self.update_schema = update_schema
        self.create_schema = create_schema
        self.get_schema = get_schema

    @classmethod
    async def get_by_id(cls, session: AsyncSession, record_id: UUID) -> Schema | None:
        """
        Retrieves a record by its ID.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            record_id (UUID): The unique identifier of the record.

        Returns:
            Schema | None: The retrieved record as a Pydantic model or None if not found.
        """
        res = await session.execute(select(cls.base_model).where(cls.base_model.id == record_id))
        obj = res.scalar_one()
        return cls.get_schema.model_validate(obj) if obj else None

    @classmethod
    async def get_by_id_no_validate(cls, session: AsyncSession, record_id: UUID) -> Schema | None:
        """
        Retrieves a record by its ID without applying Pydantic validation.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            record_id (UUID): The unique identifier of the record.

        Returns:
            Schema | None: The retrieved record or None if not found.
        """
        res = await session.execute(select(cls.base_model).where(cls.base_model.id == record_id))
        obj = res.scalar_one()
        return obj if obj else None

    @classmethod
    async def get_all(cls, session: AsyncSession, offset: int = 0, limit: int = 100) -> List[Schema]:
        """
        Retrieves all records with pagination support.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            offset (int): The starting index of records.
            limit (int): The maximum number of records to retrieve.

        Returns:
            List[Schema]: A list of retrieved records as Pydantic models.
        """
        res = await session.execute(select(cls.base_model).offset(offset).limit(limit))
        objects = res.scalars().all()
        return [cls.get_schema.model_validate(obj) for obj in objects]

    @classmethod
    async def get_filtered_by_params(cls, session: AsyncSession, **kwargs) -> list[Schema]:
        """
        Retrieves records filtered by keyword arguments.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            **kwargs: Filter parameters.

        Returns:
            list[Schema]: A list of filtered records as Pydantic models.
        """
        res = await session.execute(select(cls.base_model).filter_by(**kwargs))
        objects = res.scalars().all()
        return [cls.get_schema.model_validate(obj) for obj in objects]

    @classmethod
    async def get_filtered(cls, session: AsyncSession, filter) -> list[Schema]:
        """
        Retrieves records using a custom filter.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            filter: SQLAlchemy filter expression.

        Returns:
            list[Schema]: A list of filtered records as Pydantic models.
        """
        res = await session.execute(select(cls.base_model).filter(filter))
        objects = res.scalars().all()
        return [cls.get_schema.model_validate(obj) for obj in objects]

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> Schema:
        """
        Creates a new record in the database.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            **kwargs: Record data.

        Returns:
            Schema: The created record as a Pydantic model.
        """
        instance = cls.base_model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return cls.get_schema.model_validate(instance)

    @classmethod
    async def update(cls, session: AsyncSession, record_id: UUID, **kwargs) -> Schema:
        """
        Updates an existing record.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            record_id (UUID): The unique identifier of the record.
            **kwargs: Fields to update.

        Returns:
            Schema: The updated record as a Pydantic model.
        """
        clean_kwargs = {key: value for key, value in kwargs.items() if value is not None}
        await session.execute(update(cls.base_model).where(cls.base_model.id == record_id).values(**clean_kwargs))
        await session.commit()
        instance = await cls.get_by_id(session, record_id)
        return cls.get_schema.model_validate(instance)

    @classmethod
    async def delete(cls, session: AsyncSession, record_id: UUID):
        """
        Deletes a record by its ID.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            record_id (UUID): The unique identifier of the record.
        """
        await session.execute(delete(cls.base_model).where(cls.base_model.id == record_id))
        await session.commit()


def BaseCrudFactory(
    model: Model,
    update_schema: type(Schema),
    create_schema: type(Schema),
    get_schema: type(Schema),
) -> type(CrudFactory):
    """
    Generates a custom CRUD factory class for a given model and schemas.

    Returns:
        type[CrudFactory]: A dynamically created subclass of CrudFactory.
    """
    return type(
        "CrudFactory",
        (CrudFactory,),
        {
            "base_model": model,
            "update_schema": update_schema,
            "create_schema": create_schema,
            "get_schema": get_schema,
        },
    )
