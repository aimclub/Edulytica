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
    Class that provides CRUD operations for a given base model. Includes methods to get by ID, get all records,
    get filtered records, create, update, and delete records.
    """
    base_model: Model
    update_schema: Type[Schema]
    create_schema: Type[Schema]
    get_schema: Type[Schema]

    def __init__(self, base_model: Model,
                 update_schema: Type[Schema],
                 create_schema: Type[Schema],
                 get_schema: Type[Schema]
                 ):
        self.base_model = base_model
        self.update_schema = update_schema
        self.create_schema = create_schema
        self.get_schema = get_schema

    @classmethod
    async def get_by_id(cls, session: AsyncSession, record_id: UUID) -> Schema | None:
        res = await session.execute(select(cls.base_model).where(cls.base_model.id == record_id))
        obj = res.scalar_one()
        return cls.get_schema.model_validate(obj) if obj else None

    @classmethod
    async def get_by_id_no_validate(cls, session: AsyncSession, record_id: UUID) -> Schema | None:
        res = await session.execute(select(cls.base_model).where(cls.base_model.id == record_id))
        obj = res.scalar_one()
        return obj if obj else None

    @classmethod
    async def get_all(cls, session: AsyncSession, offset: int = 0, limit: int = 100) -> List[Schema]:
        res = await session.execute(select(cls.base_model).offset(offset).limit(limit))
        objects = res.scalars().all()
        return [cls.get_schema.model_validate(obj) for obj in objects]

    @classmethod
    async def get_filtered_by_params(cls, session: AsyncSession, **kwargs) -> list[Schema]:
        res = await session.execute(select(cls.base_model).filter_by(**kwargs))
        objects = res.scalars().all()
        return [cls.get_schema.model_validate(obj) for obj in objects]

    @classmethod
    async def get_filtered(cls, session: AsyncSession, filter) -> list[Schema]:
        res = await session.execute(select(cls.base_model).filter(filter))
        objects = res.scalars().all()
        return [cls.get_schema.model_validate(obj) for obj in objects]

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> Schema:
        instance = cls.base_model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return cls.get_schema.model_validate(instance)

    @classmethod
    async def update(cls, session: AsyncSession, record_id: UUID, **kwargs) -> Schema:
        clean_kwargs = {key: value for key, value in kwargs.items() if value is not None}
        await session.execute(update(cls.base_model).where(cls.base_model.id == record_id).values(**clean_kwargs))
        await session.commit()
        instance = await cls.get_by_id(session, record_id)
        return cls.get_schema.model_validate(instance)

    @classmethod
    async def delete(cls, session: AsyncSession, record_id: UUID):
        await session.execute(delete(cls.base_model).where(cls.base_model.id == record_id))
        await session.commit()


def BaseCrudFactory(
        model: Model,
        update_schema: type(Schema),
        create_schema: type(Schema),
        get_schema: type(Schema),
) -> type(CrudFactory):
    return type(
        "CrudFactory",
        (CrudFactory,),
        {
            "base_model": model,
            "update_schema": update_schema,
            "create_schema": create_schema,
            "get_schema": get_schema,
        }
    )
