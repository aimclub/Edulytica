import uuid
from datetime import timedelta
from fastapi import APIRouter, Body, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_401_UNAUTHORIZED
from src.common.auth.auth_bearer import refresh_token_auth, access_token_auth
from src.common.auth.helpers.utils import get_hashed_password, create_access_token, create_refresh_token, get_expiry, \
    verify_password
from src.common.config import REFRESH_TOKEN_EXPIRE_MINUTES
from src.common.database.crud.check_code_crud import CheckCodeCrud
from src.common.database.crud.token_crud import TokenCrud
from src.common.database.crud.user_crud import UserCrud
from src.common.database.crud.user_role_crud import UserRoleCrud
from src.common.database.database import get_session
from src.common.utils.check_code_utils import generate_code
from src.common.utils.default_enums import UserRoleDefault
from src.common.utils.email import send_email
from src.common.utils.logger import api_logs
from src.common.utils.moscow_datetime import datetime_now_moscow

auth_router = APIRouter()


@api_logs(auth_router.post('/registration'))
async def registration_handler(
        login: str = Body(...),
        email: str = Body(...),
        password1: str = Body(...),
        password2: str = Body(...),
        session: AsyncSession = Depends(get_session)
):
    if await UserCrud.get_filtered_by_params(
        session=session, email=email, is_active=True
    ):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail='User with such email already exists'
        )
    if await UserCrud.get_filtered_by_params(
        session=session, login=login, is_active=True
    ):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail='User with such login already exists'
        )

    if password1 != password2:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail='Passwords are not equal'
        )

    try:
        inactive_user_with_email = await UserCrud.get_filtered_by_params(
            session=session,
            email=email
        )

        user_role = await UserRoleCrud.get_filtered_by_params(
            session=session, name=UserRoleDefault.USER
        )
        if not inactive_user_with_email:
            user = await UserCrud.create(
                session=session,
                email=email,
                login=login,
                password_hash=get_hashed_password(password1),
                role_id=user_role[0].id
            )
        else:
            user = await UserCrud.update(
                session=session,
                record_id=inactive_user_with_email[0].id,
                email=email,
                login=login,
                password_hash=get_hashed_password(password1),
                role_id=user_role[0].id
            )

        code = generate_code()
        send_email(email, code)

        await CheckCodeCrud.create(
            session=session,
            code=code,
            user_id=user.id
        )

        return {'detail': 'Code has been sent'}
    except Exception as _e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(auth_router.post('/check_code'))
async def check_code_handler(
        response: Response,
        code: str = Body(..., embed=True),
        session: AsyncSession = Depends(get_session)
):
    try:
        check_code = await CheckCodeCrud.get_recent_code(
            session=session,
            code=code
        )

        if not check_code:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f'Wrong code'
            )

        await UserCrud.update(
            session=session,
            record_id=check_code.user_id,
            is_active=True
        )

        access_token = create_access_token(check_code.user_id)
        checker = uuid.uuid4()
        refresh_token = create_refresh_token(subject=check_code.user_id, checker=checker)

        await TokenCrud.create(
            session=session,
            user_id=check_code.user_id,
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
        return {'detail': 'Code is correct', 'access_token': access_token}
    except Exception as _e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(auth_router.post('login'))
async def login_handler(
        response: Response,
        login: str = Body(...),
        password: str = Body(...),
        session: AsyncSession = Depends(get_session)
):
    try:
        user = await UserCrud.get_filtered_by_params(
            session=session,
            login=login,
            is_active=True
        )

        if not user or not verify_password(password, user[0].password_hash):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail='Credentials are incorrect'
            )

        access_token = create_access_token(user[0].id)
        checker = uuid.uuid4()
        refresh_token = create_refresh_token(subject=user[0].id, checker=checker)

        await TokenCrud.create(
            session=session,
            user_id=user[0].id,
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
        return {'detail': 'Credentials are correct', 'access_token': access_token}
    except Exception as _e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(auth_router.get('/get_access'))
async def get_access_handler(
        response: Response,
        refresh_token: dict = Depends(refresh_token_auth),
        session: AsyncSession = Depends(get_session)
):
    token = await TokenCrud.get_filtered_by_params(
        session=session,
        user_id=refresh_token['user'].id,
        refresh_token=refresh_token['token'],
        checker=refresh_token['payload']['checker']
    )

    if not token or token.created_at < (datetime_now_moscow() - timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)):
        response.delete_cookie(key="refresh_token")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail='Token is incorrect'
        )

    access_token = create_access_token(refresh_token['user'].id)
    checker = uuid.uuid4()
    refresh_token_new = create_refresh_token(subject=refresh_token['user'].id, checker=checker)

    await TokenCrud.create(
        session=session,
        user_id=refresh_token['user'].id,
        refresh_token=refresh_token_new,
        checker=checker,
        status=True
    )

    response.set_cookie(
        key="refresh_token",
        value=f"Bearer {refresh_token_new}",
        httponly=True,
        expires=get_expiry(REFRESH_TOKEN_EXPIRE_MINUTES)
    )

    return {'detail': 'Token is correct', 'access_token': access_token}


@api_logs(auth_router.get('/logout'))
async def logout_handler(
        response: Response,
        refresh_token: dict = Depends(refresh_token_auth),
        session: AsyncSession = Depends(get_session)
):

    tokens = await TokenCrud.get_filtered_by_params(
        session=session,
        user_id=refresh_token['user'].id,
        checker=refresh_token['payload']['checker'],
        refresh_token=refresh_token['token']
    )
    if not tokens:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Exception in token validation")

    await TokenCrud.delete(session=session, record_id=tokens[0].id)

    response.delete_cookie(key="refresh_token")
    return {"message": "Logout Successful"}
