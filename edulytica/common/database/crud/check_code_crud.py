"""
This module defines a specialized CRUD class for handling verification codes (CheckCode)
used during user authentication processes such as registration and login.

Classes:
    CheckCodeCrud: Provides CRUD operations for the CheckCode model
"""

from datetime import timedelta, datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from edulytica.common.config import EMAIL_CODE_EXPIRE_SECONDS
from edulytica.common.database.crud.base.factory import BaseCrudFactory
from edulytica.common.database.models import CheckCode
from edulytica.common.database.schemas import CheckCodeModels
from edulytica.common.utils.moscow_datetime import datetime_now_moscow


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
        """
        Retrieves a verification code that was created within the last <N> seconds.

        This method is typically used to validate time-sensitive codes sent to users
        for registration or login confirmation.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            code (str): The verification code to search for.

        Returns:
            Optional[CheckCodeModels.Get]: A validated Pydantic model representing the CheckCode,
                                           or None if no recent code is found.
        """
        result = await session.execute(
            select(CheckCode).filter(
                CheckCode.code == code,
                CheckCode.created_at >= datetime_now_moscow() - timedelta(seconds=EMAIL_CODE_EXPIRE_SECONDS)
            )
        )

        result = result.scalar_one_or_none()

        return CheckCodeModels.Get.model_validate(result) if result else None
