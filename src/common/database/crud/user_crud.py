"""
This module defines a specialized CRUD class for working with user data.

Classes:
    UserCrud: Provides CRUD operations for the User model
"""

from typing import List
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.database.crud.base.generic_crud import GenericCrud
from src.common.database.models import User
from src.common.database.schemas.system_schemas import UserGet, UserCreate, UserUpdate


class UserCrud(
    GenericCrud[User, UserGet, UserCreate, UserUpdate]
):
    base_model = User
    get_schema = UserGet
    create_schema = UserCreate
    update_schema = UserUpdate

    @staticmethod
    async def get_active_users_by_email_or_login(
            session: AsyncSession,
            email: str,
            login: str
    ) -> List[UserGet]:
        """
        Retrieves a list of active users filtered by email or login.

        This method is useful for checking user existence during registration or login
        to ensure that credentials are not already in use.

        Args:
            session (AsyncSession): The SQLAlchemy asynchronous session.
            email (str): The email address to filter by.
            login (str): The login name to filter by.

        Returns:
            List[UserGet]: A list of active user models matching the email or login.
        """
        result = await session.execute(
            select(User).where(
                and_(
                    or_(User.email == email, User.login == login),
                    User.is_active.is_(True)
                )
            )
        )

        return [UserGet.model_validate(x) for x in result.scalars().all()]

    @staticmethod
    async def get_active_user(
            session: AsyncSession,
            login: str
    ) -> UserGet:
        result = await session.execute(
            select(User).where(
                and_(
                    or_(User.email == login, User.login == login),
                    User.is_active.is_(True)
                )
            )
        )

        user = result.scalar_one_or_none()
        return UserGet.model_validate(user) if user else None
