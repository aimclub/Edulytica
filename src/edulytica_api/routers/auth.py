import uuid
from typing import Annotated
from fastapi import APIRouter
from fastapi import Response
from fastapi.security import OAuth2PasswordRequestForm
from src.edulytica_api.crud.token_crud import TokenCrud
from src.edulytica_api.crud.user_crud import UserCrud
from src.edulytica_api.database import get_session
import src.edulytica_api.schemas.auth as auth_schemas
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from src.edulytica_api.auth.helpers.validators import password_validate
from src.edulytica_api.models.models import User
from src.edulytica_api.auth.auth_bearer import refresh_token_auth, access_token_auth
from src.edulytica_api.auth.helpers.utils import create_access_token, create_refresh_token, verify_password, \
    get_hashed_password, get_expiry
from src.edulytica_api.settings import REFRESH_TOKEN_EXPIRE_MINUTES
from src.edulytica_api.utils.logger import api_logs


auth_router = APIRouter()


@api_logs(auth_router.post('/login'))
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session)
):
    user = await UserCrud.get_filtered_by_params(session=session, username=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password")

    user = user[0]
    password_validate(form_data.password, user.password)

    access_token = create_access_token(user.id)
    checker = uuid.uuid4()
    refresh_token = create_refresh_token(subject=user.id, checker=checker)

    await TokenCrud.create(session=session, user_id=user.id, refresh_token=refresh_token, checker=checker, status=True)

    response.set_cookie(
        key="refresh_token",
        value=f"Bearer {refresh_token}",
        httponly=True,
        expires=get_expiry(REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    return auth_schemas.TokenData(access_token=access_token, refresh_token=refresh_token)


@api_logs(auth_router.post("/register"))
async def register_user(
        user: auth_schemas.UserCreate,
        session: AsyncSession = Depends(get_session)
):
    from sqlalchemy import or_

    filter_user = or_(User.username == user.username, User.email == user.email)
    existing_user = await UserCrud.get_filtered(session=session, filter=filter_user)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    encrypted_password = get_hashed_password(user.password)
    await UserCrud.create(session=session, username=user.username, email=user.email, password=encrypted_password)

    return {"message": "user created successfully"}


@api_logs(auth_router.post('/change-password'))
async def change_password(
    request: auth_schemas.changepassword,
    auth_data: Annotated[dict, Depends(access_token_auth)],
    session: AsyncSession = Depends(get_session)
):
    user = auth_data['user']
    if not verify_password(request.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password")

    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    session.add(user)
    await session.commit()

    return {"message": "Password changed successfully"}


@api_logs(auth_router.get('/refresh'))
async def refresh_token(
    response: Response,
    auth_data: Annotated[dict, Depends(refresh_token_auth)],
    session: AsyncSession = Depends(get_session)
):
    payload = auth_data['payload']
    user = auth_data['user']
    token = auth_data['token']

    tokens = await TokenCrud.get_filtered_by_params(
        session=session,
        user_id=user.id,
        checker=payload['checker'],
        refresh_token=token
    )
    if len(tokens) != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Exception in token validation")

    token = tokens[0]
    access_token = create_access_token(user.id)
    checker = uuid.uuid4()
    refresh_token = create_refresh_token(subject=user.id, checker=checker)

    await TokenCrud.update(
        session=session,
        record_id=token.id,
        refresh_token=refresh_token,
        checker=checker,
        status=True
    )

    response.set_cookie(
        key="refresh_token",
        value=f"Bearer {refresh_token}",
        httponly=True,
        expires=get_expiry(REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    return auth_schemas.TokenData(access_token=access_token, refresh_token=refresh_token)


@api_logs(auth_router.get('/logout'))
async def logout(
    response: Response,
    auth_data: Annotated[dict, Depends(refresh_token_auth)],
    session: AsyncSession = Depends(get_session)
):
    token = auth_data['token']
    payload = auth_data['payload']
    user = auth_data['user']

    tokens = await TokenCrud.get_filtered_by_params(
        session=session,
        user_id=user.id,
        checker=payload['checker'],
        refresh_token=token
    )
    if len(tokens) != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Exception in token validation")

    token = tokens[0]
    await TokenCrud.delete(session=session, record_id=token.id)

    response.delete_cookie(key="refresh_token")
    return {"message": "Logout Successfully"}
