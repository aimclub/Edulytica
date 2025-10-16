"""
This module defines a specialized CRUD class for handling verification codes (CheckCode)
used during user authentication processes such as registration and login.

Classes:
    CheckCodeCrud: Provides CRUD operations for the CheckCode model
"""
from datetime import timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.config import EMAIL_CODE_EXPIRE_SECONDS
from src.common.database.crud.base.generic_crud import GenericCrud
from src.common.database.models import CheckCode
from src.common.database.schemas.system_schemas import CheckCodeGet, CheckCodeCreate, CheckCodeUpdate
from src.common.utils.moscow_datetime import datetime_now_moscow


class CheckCodeCrud(
    GenericCrud[CheckCode, CheckCodeGet, CheckCodeCreate, CheckCodeUpdate]
):
    base_model = CheckCode
    get_schema = CheckCodeGet
    create_schema = CheckCodeCreate
    update_schema = CheckCodeUpdate

    @staticmethod
    async def get_recent_code(session: AsyncSession, code: str) -> Optional[CheckCodeGet]:
        """
        Retrieves a verification code that was created within the last <N> seconds.

        This method is typically used to validate time-sensitive codes sent to users
        for registration or login confirmation.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            code (str): The verification code to search for.

        Returns:
            Optional[CheckCodeGet]: A validated Pydantic model representing the CheckCode,
                                           or None if no recent code is found.
        """
        result = await session.execute(
            select(CheckCode).filter(
                CheckCode.code == code,
                CheckCode.created_at >= datetime_now_moscow() - timedelta(seconds=EMAIL_CODE_EXPIRE_SECONDS)
            )
        )

        result = result.scalar_one_or_none()

        return CheckCodeGet.model_validate(result) if result else None
