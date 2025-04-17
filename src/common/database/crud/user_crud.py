"""
This module defines a specialized CRUD class for working with user data.

Classes:
    UserCrud: Provides CRUD operations for the User model
"""

from typing import List
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.database.crud.base.factory import BaseCrudFactory
from src.common.database.models import User
from src.common.database.schemas import UserModels


class UserCrud(
    BaseCrudFactory(
        model=User,
        update_schema=UserModels.Update,
        create_schema=UserModels.Create,
        get_schema=UserModels.Get,
    )
):
    @staticmethod
    async def get_active_user_by_email_or_login(
            session: AsyncSession,
            email: str,
            login: str
    ) -> List[UserModels.Get]:
        """
        Retrieves a list of active users filtered by email or login.

        This method is useful for checking user existence during registration or login
        to ensure that credentials are not already in use.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            email (str): The email address to filter by.
            login (str): The login name to filter by.

        Returns:
            List[UserModels.Get]: A list of active user models matching the email or login.
        """
        result = await session.execute(
            select(User).where(
                and_(
                    or_(User.email == email, User.login == login),
                    User.is_active.is_(True)
                )
            )
        )

        return [UserModels.Get.model_validate(x) for x in result.scalars().all()]
