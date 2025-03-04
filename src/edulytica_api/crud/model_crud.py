from typing import Optional, Dict
from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession
from src.edulytica_api.crud.factory import BaseCrudFactory, Model
from src.edulytica_api.models.updated_models import Ticket
from src.edulytica_api.schemas import ModelModels


class ModelCrud(

    BaseCrudFactory(
        model=Model,
        update_schema=ModelModels.Update,
        create_schema=ModelModels.Create,
        get_schema=ModelModels.Get,
    )
):
    @staticmethod
    async def get_model_statistics_by_tag(model_tag: str, session: AsyncSession) -> Optional[Dict]:
        total_tickets_subq = select(func.count()).select_from(Ticket).scalar_subquery()

        result = await session.execute(
            select(
                func.count(Ticket.id).label("usage_count"),
                (func.count(Ticket.id) * 100.0 / total_tickets_subq).label("usage_percentage"),
                func.avg(Ticket.rate).label("avg_rating"),
                (func.count(case((Ticket.rate is not None, 1))) * 100.0 / func.nullif(func.count(Ticket.id), 0)).label(
                    "rating_percentage")
            )
            .select_from(Ticket)
            .join(Model, Model.id == Ticket.model_id)
            .where(Model.tag == model_tag)
        )

        stats = result.one_or_none()
        if not stats:
            return None

        return {
            "usage_count": stats.usage_count,
            "usage_percentage": stats.usage_percentage,
            "avg_rating": stats.avg_rating,
            "rating_percentage": stats.rating_percentage,
        }
