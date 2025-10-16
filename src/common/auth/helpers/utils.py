"""
This module provides utilities for handling JWT authentication in a FastAPI application.
It includes functions for password hashing, JWT encoding and decoding, and token-based authentication.
"""

import time
from datetime import datetime, timedelta
from typing import Union, Any, Optional
from jose import jwt
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED
from src.common.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, JWT_SECRET_KEY, \
    JWT_REFRESH_SECRET_KEY, REFRESH_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request, HTTPException
from fastapi.security.utils import get_authorization_scheme_param

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TOKEN_TYPE_FIELD = 'token_type'
ACCESS_TOKEN_TYPE = 'access'
REFRESH_TOKEN_TYPE = 'refresh'


def get_hashed_password(password: str) -> str:
    """
    Hashes a password using bcrypt.

    Args:
        password (str): Plain-text password.

    Returns:
        str: Hashed password.
    """
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    """
    Verifies a plain-text password against its hashed version.

    Args:
        password (str): Plain-text password.
        hashed_pass (str): Hashed password.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return password_context.verify(password, hashed_pass)


def encode_jwt(
        payload: dict,
        private_key: str = JWT_SECRET_KEY,
        algorithm: str = ALGORITHM,
        expires_delta: Optional[timedelta] = None,
        expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    """
    Encodes a payload into a JWT token.

    Args:
        payload (dict): Data to encode.
        private_key (str): Secret key for signing the token.
        algorithm (str): JWT signing algorithm.
        expires_delta (Optional[timedelta]): Expiration duration.
        expires_minutes (int): Expiration duration in minutes if expires_delta is not provided.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = payload.copy()
    now = datetime.utcnow()
    expires = now + (expires_delta if expires_delta else timedelta(minutes=expires_minutes))
    to_encode.update(exp=expires, iat=now)
    return jwt.encode(to_encode, private_key, algorithm=algorithm)


def create_jwt(
        token_data: dict,
        token_type: str = ACCESS_TOKEN_TYPE,
        jwt_secret: str = JWT_SECRET_KEY,
        expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
        expires_delta: Optional[timedelta] = None):
    """
    Creates a JWT token with specified token type.

    Args:
        token_data (dict): Data to include in the token.
        token_type (str): Type of token (access or refresh).
        jwt_secret (str): Secret key for signing the token.
        expires_minutes (int): Expiration duration in minutes.
        expires_delta (Optional[timedelta]): Expiration duration override.

    Returns:
        str: JWT token.
    """
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(payload=jwt_payload, private_key=jwt_secret, algorithm=ALGORITHM,
                      expires_minutes=expires_minutes, expires_delta=expires_delta)


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates an access token for a given subject.

    Args:
        subject (Union[str, Any]): The subject identifier for the token.
        expires_delta (Optional[timedelta]): Expiration duration override.

    Returns:
        str: Encoded access token.
    """
    return create_jwt(
        token_data={
            "sub": str(subject)},
        token_type=ACCESS_TOKEN_TYPE,
        jwt_secret=JWT_SECRET_KEY,
        expires_delta=expires_delta,
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(subject: Union[str, Any], checker: Union[str, Any],
                         expires_delta: Optional[int] = None) -> str:
    """
    Creates a refresh token for a given subject and checker.

    Args:
        subject (Union[str, Any]): The subject identifier for the token.
        checker (Union[str, Any]): Additional data for verification.
        expires_delta (Optional[int]): Expiration duration override.

    Returns:
        str: Encoded refresh token.
    """
    return create_jwt(
        token_data={
            "sub": str(subject),
            'checker': str(checker)},
        token_type=REFRESH_TOKEN_TYPE,
        jwt_secret=JWT_REFRESH_SECRET_KEY,
        expires_delta=expires_delta,
        expires_minutes=REFRESH_TOKEN_EXPIRE_MINUTES)


def get_expiry(token_exp: int) -> str:
    """
    Calculates the expiration time in GMT format.

    Args:
        token_exp (int): Expiration time in minutes.

    Returns:
        str: Expiration time formatted as GMT.
    """
    expires = time.gmtime(time.time() + token_exp * 60)
    return time.strftime('%a, %d-%b-%Y %T GMT', expires)


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    """
    Custom OAuth2PasswordBearer implementation that supports token retrieval from cookies.
    """

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        if request.url.path in ['/get_access', '/logout']:
            authorization = request.cookies.get("refresh_token")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        return param
