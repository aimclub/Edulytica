import uuid
from typing import Annotated

from fastapi import Request

from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from src.edulytica_api.crud.token_crud import TokenCrud
from src.edulytica_api.crud.user_crud import UserCrud
from src.edulytica_api.database import get_session
import src.edulytica_api.schemas.auth as auth_schemas
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from src.edulytica_api.helpers.validators import password_validate
from src.edulytica_api.models.auth import User
from src.edulytica_api.routers.auth_bearer import oauth2_scheme, refresh_token_auth, \
    access_token_auth
from src.edulytica_api.helpers.utils import create_access_token, create_refresh_token, verify_password, \
    get_hashed_password

auth_router = APIRouter()


@auth_router.post('/login')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: Session = Depends(get_session)):
    user = UserCrud.get_filtered_by_params(session=db, username=form_data.username)
    if user is None or len(user) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    user = user[0]
    password_validate(form_data.password, user.password)
    access_token = create_access_token(user.id)
    checker = uuid.uuid4()
    refresh_token = create_refresh_token(subject=user.id, checker=checker)
    TokenCrud.create(session=db, user_id=user.id, refresh_token=refresh_token, checker=checker, status=True)
    return auth_schemas.TokenData(access_token=access_token,
                                  refresh_token=refresh_token)


@auth_router.post("/register")
async def register_user(user: auth_schemas.UserCreate, db: Session = Depends(get_session)):
    from sqlalchemy import or_
    filter_user = or_(User.username == user.username, User.email == user.email)
    existing_user = UserCrud.get_filtered(session=db, filter=filter_user)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    encrypted_password = get_hashed_password(user.password)

    UserCrud.create(session=db, username=user.username, email=user.email, password=encrypted_password)

    return {"message": "user created successfully"}


@auth_router.post('/change-password')
def change_password(request: auth_schemas.changepassword,
                    auth_data: Annotated[dict, Depends(access_token_auth)],
                    session: Session = Depends(get_session)):
    user = auth_data['user']
    if not verify_password(request.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password")

    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    session.commit()

    return {"message": "Password changed successfully"}


@auth_router.get('/refresh')
async def refresh_token(auth_data: Annotated[dict, Depends(refresh_token_auth)],
                        session: Session = Depends(get_session)):
    payload = auth_data['payload']
    user = auth_data['user']
    token = auth_data['token']
    tokens = TokenCrud.get_filtered_by_params(session=session, user_id=user.id, checker=payload['checker'],
                                              refresh_token=token)
    if len(tokens) != 1:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Exception in token validation")
    token = tokens[0]
    access_token = create_access_token(user.id)
    checker = uuid.uuid4()
    refresh_token = create_refresh_token(subject=user.id, checker=checker)
    TokenCrud.update(session=session, record_id=token.id, refresh_token=refresh_token, checker=checker, status=True)

    return auth_schemas.TokenData(access_token=access_token,
                                  refresh_token=refresh_token)


@auth_router.post('/logout')
async def logout(request: Request, auth_data: Annotated[dict, Depends(refresh_token_auth)], session: Session = Depends(get_session)):
    token = auth_data['token']
    payload = auth_data['payload']
    user = auth_data['user']
    tokens = TokenCrud.get_filtered_by_params(session=session, user_id=user.id, checker=payload['checker'],
                                              refresh_token=token)
    if len(tokens) != 1:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Exception in token validation")
    token = tokens[0]
    TokenCrud.delete(session=session, record_id = token.id)
    return {"message": "Logout Successfully"}
