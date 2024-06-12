import os
from datetime import datetime, timedelta, timezone
from typing import Union, Any

from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext

from src.edulytica_api.settings import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, JWT_SECRET_KEY, \
    REFRESH_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_SECRET_KEY

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TOKEN_TYPE_FIELD = 'token_type'
ACCESS_TOKEN_TYPE = 'access'
REFRESH_TOKEN_TYPE = 'refresh'


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def encode_jwt(
        payload: dict,
        private_key: str = JWT_SECRET_KEY,
        algorithm: str = ALGORITHM,
        expires_delta: timedelta | None = None,
        expires_minutres: int = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expires_delta is not None:
        expires = now + expires_delta
    else:
        expires = now + timedelta(minutes=expires_minutres)
    to_encode.update(
        exp=expires,
        iat=now
    )
    return jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm
    )


def create_jwt(token_data: dict, token_type=ACCESS_TOKEN_TYPE, jwt_secret=JWT_SECRET_KEY,
               expires_delta: timedelta | None = None):
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(payload=jwt_payload, private_key=jwt_secret, algorithm=ALGORITHM,
                      expires_minutres=ACCESS_TOKEN_EXPIRE_MINUTES, expires_delta=expires_delta)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    to_encode = {"sub": str(subject)}
    return create_jwt(token_data=to_encode, token_type=ACCESS_TOKEN_TYPE, jwt_secret=JWT_SECRET_KEY,
                      expires_delta=expires_delta)


def create_refresh_token(subject: Union[str, Any], checker: Union[str, Any], expires_delta: int = None) -> str:
    to_encode = {"sub": str(subject), 'checker': str(checker)}
    return create_jwt(token_data=to_encode, token_type=REFRESH_TOKEN_TYPE, jwt_secret=JWT_REFRESH_SECRET_KEY,
                      expires_delta=expires_delta)
