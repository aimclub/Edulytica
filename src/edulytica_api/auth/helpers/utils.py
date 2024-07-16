import time
from datetime import datetime, timedelta
from typing import Union, Any

from jose import jwt
from passlib.context import CryptContext
from starlette.status import HTTP_401_UNAUTHORIZED

from src.edulytica_api.settings import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, JWT_SECRET_KEY, \
    JWT_REFRESH_SECRET_KEY, REFRESH_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2, OAuth2PasswordBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param
from fastapi import HTTPException
from fastapi import status
from typing import Optional
from typing import Dict

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
        expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expires_delta is not None:
        expires = now + expires_delta
    else:
        expires = now + timedelta(minutes=expires_minutes)
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
               expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
               expires_delta: timedelta | None = None):
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(payload=jwt_payload, private_key=jwt_secret, algorithm=ALGORITHM,
                      expires_minutes=expires_minutes, expires_delta=expires_delta)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    to_encode = {"sub": str(subject)}
    return create_jwt(token_data=to_encode, token_type=ACCESS_TOKEN_TYPE, jwt_secret=JWT_SECRET_KEY,
                      expires_delta=expires_delta, expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(subject: Union[str, Any], checker: Union[str, Any], expires_delta: int = None) -> str:
    to_encode = {"sub": str(subject), 'checker': str(checker)}
    return create_jwt(token_data=to_encode, token_type=REFRESH_TOKEN_TYPE, jwt_secret=JWT_REFRESH_SECRET_KEY,
                      expires_delta=expires_delta, expires_minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

def get_expiry(token_exp):
    expires = time.gmtime(time.time() + token_exp * 60)
    return time.strftime('%a, %d-%b-%Y %T GMT', expires)

class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        if request.url.path in ['/refresh','/logout']:
            authorization: str = request.cookies.get("refresh_token")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param
