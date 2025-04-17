"""
This module defines authentication-related API endpoints for user registration, login,
logout, token refreshing, and email code verification in a FastAPI application.

The endpoints handle user authentication using JWT access and refresh tokens,
email verification via confirmation codes, and secure session handling through HTTP-only cookies.

Routes:
    POST /registration: Registers a new user and sends a verification code via email.
    POST /check_code: Verifies the confirmation code and activates the user account.
    POST /login: Authenticates user credentials and returns access and refresh tokens.
    GET /get_access: Renews access and refresh tokens using a valid refresh token.
    GET /logout: Revokes the refresh token and logs out the user.
"""

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
    """
    Registers a new user and sends a confirmation code to their email address.

    Validates that the email and login are unique among active users,
    checks that the passwords match, and creates a new inactive user.
    Then sends a confirmation code via email.

    Args:
        login (str): Desired login of the user.
        email (str): User's email address.
        password1 (str): Password input.
        password2 (str): Password confirmation.
        session (AsyncSession): Asynchronous database session.

    Returns:
        dict: A message confirming the code has been sent.

    Raises:
        HTTPException: On duplicate login/email, password mismatch, or internal errors.
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
    """
    Verifies a confirmation code and activates the corresponding user account.

    If the code is valid and recent, marks the user as active and issues
    access and refresh tokens. Sets the refresh token in an HTTP-only cookie.

    Args:
        response (Response): FastAPI response object for setting cookies.
        code (str): Confirmation code sent to the user's email.
        session (AsyncSession): Asynchronous database session.

    Returns:
        dict: Message indicating success and the access token.

    Raises:
        HTTPException: On invalid code or internal errors.
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

        if await UserCrud.get_active_user_by_email_or_login(
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


@api_logs(auth_router.post('/login'))
async def login_handler(
        response: Response,
        login: str = Body(...),
        password: str = Body(...),
        session: AsyncSession = Depends(get_session)
):
    """
    Authenticates a user and issues new access and refresh tokens.

    Validates credentials, sets the refresh token in an HTTP-only cookie,
    and returns the access token in the response.

    Args:
        response (Response): FastAPI response object for setting cookies.
        login (str): User login.
        password (str): User password.
        session (AsyncSession): Asynchronous database session.

    Returns:
        dict: Message confirming successful authentication and the access token.

    Raises:
        HTTPException: On incorrect credentials or internal errors.
    """
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
    """
    Refreshes the access token using a valid refresh token.

    Validates the existing refresh token, issues a new one along with a new access token,
    and updates the stored token in the database.

    Args:
        response (Response): FastAPI response object for updating the cookie.
        refresh_token (dict): Parsed and validated refresh token data.
        session (AsyncSession): Asynchronous database session.

    Returns:
        dict: Message confirming token renewal and the new access token.

    Raises:
        HTTPException: If the refresh token is invalid or expired.
    """
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
    """
    Logs out the user by revoking the associated refresh token.

    Deletes the refresh token from the database and clears it from cookies.

    Args:
        response (Response): FastAPI response object for clearing cookies.
        refresh_token (dict): Parsed and validated refresh token data.
        session (AsyncSession): Asynchronous database session.

    Returns:
        dict: Message confirming logout.

    Raises:
        HTTPException: If the token is invalid or missing in the database.
    """
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
