from typing import Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import update, select, delete
from sqlalchemy.ext.declarative import declarative_base

from src.edulytica_api.database import SessionLocal

Schema = TypeVar("Schema", bound=BaseModel, covariant=True)
Model = TypeVar("Model", bound=declarative_base())


class CrudFactory:
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
    def get_by_id(cls, session: SessionLocal, record_id: int) -> Schema | None:
        res = session.execute(select(cls.base_model).where(cls.base_model.id == record_id))
        obj = res.scalar_one()
        return cls.get_schema.model_validate(obj) if obj else None

    @classmethod
    def get_all(cls, session: SessionLocal, offset: int = 0, limit: int = 100) -> list[Schema]:
        res = session.execute(select(cls.base_model).offset(offset).limit(limit))
        objects = res.scalars().all()
        return [cls.get_schema.model_validate(obj) for obj in objects]

    @classmethod
    def get_filtered_by_params(cls, session: SessionLocal, **kwargs) -> list[Schema]:
        res = session.execute(select(cls.base_model).filter_by(**kwargs))
        objects = res.scalars().all()
        return [cls.get_schema.model_validate(obj) for obj in objects]

    @classmethod
    def get_filtered(cls, session: SessionLocal, filter) -> list[Schema]:
        res = session.execute(select(cls.base_model).filter(filter))
        objects = res.scalars().all()
        return [cls.get_schema.model_validate(obj) for obj in objects]

    @classmethod
    def create(cls, session: SessionLocal, **kwargs) -> Schema:
        instance = cls.base_model(**kwargs)
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return cls.get_schema.model_validate(instance)

    @classmethod
    def update(cls, session: SessionLocal, record_id: int, **kwargs) -> Schema:
        clean_kwargs = {key: value for key, value in kwargs.items() if value is not None}
        session.execute(update(cls.base_model).where(cls.base_model.id == record_id).values(**clean_kwargs))
        session.commit()
        return  cls.get_by_id(session, record_id)

    @classmethod
    def delete(cls, session: SessionLocal, record_id: int):
        session.execute(delete(cls.base_model).where(cls.base_model.id == record_id))
        session.commit()


def BaseCrudFactory(
        model: Model,
        update_schema: Type[Schema],
        create_schema: Type[Schema],
        get_schema: Type[Schema],
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

