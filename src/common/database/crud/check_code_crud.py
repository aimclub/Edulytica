from datetime import timedelta, datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.database.crud.base.factory import BaseCrudFactory
from src.common.database.models import CheckCode
from src.common.database.schemas import CheckCodeModels


class CheckCodeCrud(

    BaseCrudFactory(
        model=CheckCode,
        update_schema=CheckCodeModels.Update,
        create_schema=CheckCodeModels.Create,
        get_schema=CheckCodeModels.Get,
    )
):
    @staticmethod
    async def get_recent_code(session: AsyncSession, code: str) -> Optional[CheckCodeModels.Get]:
        result = await session.execute(
            select(CheckCode).filter(
                CheckCode.code == code,
                CheckCode.created_at >= datetime.now() - timedelta(seconds=60)
            )
        )

        result = result.scalar_one_or_none()

        return CheckCodeModels.Get.model_validate(result) if result else None
