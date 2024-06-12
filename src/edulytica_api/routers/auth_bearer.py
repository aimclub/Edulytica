from typing import Annotated

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from src.edulytica_api.crud.user_crud import UserCrud
from src.edulytica_api.database import get_session
from src.edulytica_api.settings import ALGORITHM, JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY
from src.edulytica_api.helpers.utils import TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
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


class AuthDataGetterFromToken():
    def __init__(self, token_type, secret_key):
        self.token_type = token_type
        self.secret_key = secret_key

    def __call__(self, token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[ALGORITHM])
            if self.token_type_validate(payload, self.token_type):
                user = self.user_check(payload=payload, session=session)
                return {"user": user,
                        "payload": payload,
                        "token": token}
        except JWTError:
            raise credentials_exception

    @staticmethod
    def user_check(payload, session: Session):
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = UserCrud.get_by_id(session=session, record_id=user_id)
        if user is None:
            raise credentials_exception
        if user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user

    @staticmethod
    def token_type_validate(payload, token_type):
        if payload.get(TOKEN_TYPE_FIELD) == token_type:
            return True
        else:
            raise token_type_exception


refresh_token_auth = AuthDataGetterFromToken(token_type=REFRESH_TOKEN_TYPE, secret_key=JWT_REFRESH_SECRET_KEY)
access_token_auth = AuthDataGetterFromToken(token_type=ACCESS_TOKEN_TYPE, secret_key=JWT_SECRET_KEY)