"""
This module provides authentication and authorization utilities for handling JWT tokens in FastAPI applications.
It includes functionality for verifying tokens, extracting user information, and password hashing.
"""

from typing import Annotated
from fastapi import HTTPException, Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from edulytica.common.database.crud.user_crud import UserCrud
from edulytica.common.database.database import get_session
from edulytica.common.config import ALGORITHM, JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY
from edulytica.common.auth.helpers.utils import TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, \
    OAuth2PasswordBearerWithCookie


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

token_type_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate token type",
    headers={"WWW-Authenticate": "Bearer"},
)


class AuthDataGetterFromToken:
    """
    Handles authentication and user extraction from JWT tokens.

    Attributes:
        token_type (str): Expected type of the token (access or refresh).
        secret_key (str): Secret key used for decoding the token.
    """

    def __init__(self, token_type: str, secret_key: str):
        self.token_type = token_type
        self.secret_key = secret_key

    async def __call__(
            self,
            token: Annotated[str, Depends(oauth2_scheme)],
            session: AsyncSession = Depends(get_session)
    ):
        """
        Validates the token and retrieves the user.

        Args:
            token (str): JWT token from the request.
            session (AsyncSession): Database session for retrieving user information.

        Returns:
            dict: Contains user object, payload, and token if authentication is successful.

        Raises:
            HTTPException: If the token is invalid or user authentication fails.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[ALGORITHM])
            if self.token_type_validate(payload, self.token_type):
                user = await self.user_check(payload=payload, session=session)
                return {"user": user, "payload": payload, "token": token}
        except JWTError:
            raise credentials_exception

    @staticmethod
    async def user_check(payload: dict, session: AsyncSession):
        """
        Retrieves the user based on the token payload.

        Args:
            payload (dict): Decoded JWT payload.
            session (AsyncSession): Database session for retrieving user information.

        Returns:
            User: The authenticated user object.

        Raises:
            HTTPException: If the user ID is missing, user does not exist, or user is inactive.
        """
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = await UserCrud.get_by_id(session=session, record_id=user_id)
        if user is None:
            raise credentials_exception
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user

    @staticmethod
    def token_type_validate(payload: dict, token_type: str):
        """
        Validates that the token type matches the expected type.

        Args:
            payload (dict): Decoded JWT payload.
            token_type (str): Expected token type.

        Returns:
            bool: True if the token type is valid.

        Raises:
            HTTPException: If the token type is incorrect.
        """
        if payload.get(TOKEN_TYPE_FIELD) == token_type:
            return True
        else:
            raise token_type_exception


# Authentication handlers for different token types
refresh_token_auth = AuthDataGetterFromToken(
    token_type=REFRESH_TOKEN_TYPE,
    secret_key=JWT_REFRESH_SECRET_KEY)
access_token_auth = AuthDataGetterFromToken(token_type=ACCESS_TOKEN_TYPE, secret_key=JWT_SECRET_KEY)
