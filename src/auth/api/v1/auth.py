"""
Description
    Authentication API for user sign-up with email verification, sign-in,
    JWT issuance/rotation, and logout in a FastAPI application. Access tokens
    are returned in the response body; refresh tokens are set as HTTP-only cookies.

Routes:
    POST /registration  — create inactive user, send confirmation code to email.
    POST /check_code    — verify code, activate account, issue tokens (refresh in cookie).
    POST /login         — authenticate and issue tokens (refresh in cookie).
    GET  /get_access    — rotate refresh token and issue new access token.
    GET  /logout        — revoke refresh token and clear cookie.
"""

import uuid
from datetime import timedelta
from fastapi import APIRouter, Body, Depends, HTTPException, Response, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_401_UNAUTHORIZED
from src.common.auth.auth_bearer import refresh_token_auth
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

auth_v1 = APIRouter(prefix='/api/auth/v1', tags=['auth'])


@api_logs(auth_v1.post('/registration'), exclude_args=['background_tasks', 'password1', 'password2'])
async def registration_handler(
        background_tasks: BackgroundTasks,
        login: str = Body(...),
        email: str = Body(...),
        password1: str = Body(...),
        password2: str = Body(...),
        session: AsyncSession = Depends(get_session),
):
    """
    Description
        Register a new user and send an email confirmation code.

    Args:
        login (str): Desired unique login.
        email (str): User email.
        password1 (str): Password.
        password2 (str): Password confirmation.
        background_tasks (BackgroundTasks): Background task runner.
        session (AsyncSession): Database session.

    Responses:
        200: {"detail": "Code has been sent"}
        400: {"detail": "User with such email already exists" |
                       "User with such login already exists" |
                       "Passwords are not equal"}
        500: {"detail": "500 ERR: <message>"}
    """
    try:
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

        user_role = await UserRoleCrud.get_filtered_by_params(
            session=session, name=UserRoleDefault.USER
        )

        user = await UserCrud.create(
            session=session,
            email=email,
            login=login,
            password_hash=get_hashed_password(password1),
            role_id=user_role[0].id
        )

        code = generate_code()

        await CheckCodeCrud.create(
            session=session,
            code=code,
            user_id=user.id
        )

        background_tasks.add_task(send_email, to_email=email, code=code)

        return {'detail': 'Code has been sent'}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(auth_v1.post('/check_code'), exclude_args=['response', 'code'])
async def check_code_handler(
        response: Response,
        code: str = Body(..., embed=True),
        session: AsyncSession = Depends(get_session)
):
    """
    Description
        Verify a confirmation code, activate the account, and issue tokens.
        Access token is returned in the body; refresh token is set as an HTTP-only cookie.

    Args:
        code (str): Confirmation code from email.
        response (Response): Response for setting cookies.
        session (AsyncSession): Database session.

    Responses:
        200: {"detail": "Code is correct", "access_token": "<JWT>"}
        400: {"detail": "Wrong code" |
                       "User with such email or login already is active"}
        500: {"detail": "500 ERR: <message>"}
    """
    try:
        check_code = await CheckCodeCrud.get_recent_code(
            session=session,
            code=code
        )

        if not check_code:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Wrong code'
            )

        inactive_user = await UserCrud.get_by_id(
            session=session,
            record_id=check_code.user_id
        )

        if await UserCrud.get_active_users_by_email_or_login(
            session=session,
            login=inactive_user.login,
            email=inactive_user.email
        ):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='User with such email or login already is active'
            )

        await UserCrud.update(
            session=session,
            record_id=inactive_user.id,
            is_active=True
        )

        access_token = create_access_token(check_code.user_id)
        checker = uuid.uuid4()
        refresh_token = create_refresh_token(subject=check_code.user_id, checker=checker)

        await TokenCrud.create(
            session=session,
            user_id=check_code.user_id,
            refresh_token=refresh_token,
            checker=checker
        )

        response.set_cookie(
            key="refresh_token",
            value=f"Bearer {refresh_token}",
            httponly=True,
            expires=get_expiry(REFRESH_TOKEN_EXPIRE_MINUTES)
        )
        return {'detail': 'Code is correct', 'access_token': access_token}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(auth_v1.post('/login'), exclude_args=['response', 'password'])
async def login_handler(
        response: Response,
        login: str = Body(...),
        password: str = Body(...),
        session: AsyncSession = Depends(get_session)
):
    """
    Description
        Authenticate an active user and issue tokens.
        Access token is returned in the body; refresh token is set as an HTTP-only cookie.

    Args:
        login (str): User login.
        password (str): User password.
        response (Response): Response for setting cookies.
        session (AsyncSession): Database session.

    Responses:
        200: {"detail": "Credentials are correct", "access_token": "<JWT>"}
        401: {"detail": "Credentials are incorrect"}
        500: {"detail": "500 ERR: <message>"}
    """
    try:
        user = await UserCrud.get_active_user(
            session=session,
            login=login
        )

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail='Credentials are incorrect'
            )

        access_token = create_access_token(user.id)
        checker = uuid.uuid4()
        refresh_token = create_refresh_token(subject=user.id, checker=checker)

        await TokenCrud.create(
            session=session,
            user_id=user.id,
            refresh_token=refresh_token,
            checker=checker
        )

        response.set_cookie(
            key="refresh_token",
            value=f"Bearer {refresh_token}",
            httponly=True,
            expires=get_expiry(REFRESH_TOKEN_EXPIRE_MINUTES)
        )
        return {'detail': 'Credentials are correct', 'access_token': access_token}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(auth_v1.get('/get_access'), exclude_args=['response', 'refresh_token'])
async def get_access_handler(
        response: Response,
        refresh_token: dict = Depends(refresh_token_auth),
        session: AsyncSession = Depends(get_session)
):
    """
    Description
        Rotate the refresh token and issue a new access token using a valid
        refresh token from the HTTP-only cookie.

    Args:
        refresh_token (dict): Parsed and validated refresh token data.
        response (Response): Response for updating cookies.
        session (AsyncSession): Database session.

    Responses:
        200: {"detail": "Token is correct", "access_token": "<JWT>"}
        400: {"detail": "Token is incorrect"}
        500: {"detail": "500 ERR: <message>"}
    """
    try:
        token = await TokenCrud.get_filtered_by_params(
            session=session,
            user_id=refresh_token['user'].id,
            refresh_token=refresh_token['token'],
            checker=refresh_token['payload']['checker']
        )

        if not token or token[0].created_at < (
                datetime_now_moscow() -
                timedelta(
                    minutes=REFRESH_TOKEN_EXPIRE_MINUTES)):
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
            checker=checker
        )

        response.set_cookie(
            key="refresh_token",
            value=f"Bearer {refresh_token_new}",
            httponly=True,
            expires=get_expiry(REFRESH_TOKEN_EXPIRE_MINUTES)
        )

        return {'detail': 'Token is correct', 'access_token': access_token}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(auth_v1.get('/logout'), exclude_args=['response', 'refresh_token'])
async def logout_handler(
        response: Response,
        refresh_token: dict = Depends(refresh_token_auth),
        session: AsyncSession = Depends(get_session)
):
    """
    Description
        Revoke the current refresh token and clear the HTTP-only cookie.

    Args:
        refresh_token (dict): Parsed and validated refresh token data.
        response (Response): Response for clearing cookies.
        session (AsyncSession): Database session.

    Responses:
        200: {"detail": "Logout Successful"}
        401: {"detail": "Exception in token validation"}
        500: {"detail": "500 ERR: <message>"}
    """
    try:
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
        return {"detail": "Logout Successful"}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )
