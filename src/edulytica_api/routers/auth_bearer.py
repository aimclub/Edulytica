from typing import Annotated


from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from src.edulytica_api.crud.user_crud import UserCrud
from src.edulytica_api.crud.token_crud import TokenCrud
from src.edulytica_api.database import get_session
from src.edulytica_api.models.auth import User
from src.edulytica_api.settings import ALGORITHM, JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await UserCrud.get_by_id(session=db, record_id=user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_refresh(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        checker = payload.get('checker')
        if user_id is None or checker is None:
            raise credentials_exception
        user = await UserCrud.get_by_id(session=db, record_id=user_id)
        token = await TokenCrud.get_filtered_by_params(session=db,user_id=user.id, refresh_token=token, checker=checker)
    except JWTError:
        raise credentials_exception
    return {'user': user, 'refresh_token': token[0]}
async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_user_refresh(
        data: Annotated[dict, Depends(get_current_user_refresh)],
):
    if (data['user'].disabled):
        raise HTTPException(status_code=400, detail="Inactive user")
    return data