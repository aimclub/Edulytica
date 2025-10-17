"""
Description
    Account API for retrieving the authenticated user profile, editing basic profile fields,
    and changing the password. All endpoints require a valid JWT access token.

Routes:
    GET   /           — Return the authenticated user object from the token.
    PATCH /           — Update profile fields (name, surname, organization).
    POST  /password   — Change password after verifying the old one.
"""


from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_204_NO_CONTENT, HTTP_200_OK
from src.common.auth.auth_bearer import access_token_auth
from src.common.auth.helpers.utils import verify_password, get_hashed_password
from src.common.database.crud.user_crud import UserCrud
from src.common.database.database import get_session
from src.common.utils.logger import api_logs
from src.edulytica_api.schemas.account_schemas import EditProfileRequest, ChangePasswordRequest


account_v1 = APIRouter(prefix="/api/account/v1", tags=["account"])


@api_logs(account_v1.get("", status_code=HTTP_200_OK))
async def get_account(
    auth_data: dict = Depends(access_token_auth)
):
    """
    Description
        Return the authenticated user object extracted from the access token.

    Args:
        auth_data (dict): Authenticated user data injected by the access token dependency.

    Responses:
        200: The user object (dict) as stored on the token.

    Raises:
        HTTPException: If the token is invalid or an unexpected error occurs.
    """
    try:
        return auth_data['user']
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=500,
            detail=f"500 ERR: {_e}"
        )


@api_logs(account_v1.patch("", status_code=HTTP_204_NO_CONTENT))
async def edit_profile(
    auth_data: dict = Depends(access_token_auth),
    data: EditProfileRequest = Body(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Description
        Update one or more profile fields (name, surname, organization) for the authenticated user.

    Args:
        auth_data (dict): Authenticated user data.
        data (EditProfileRequest): Optional fields to update (at least one must be provided).
        session (AsyncSession): Database session.

    Responses:
        204: Profile updated successfully (no content).
        400: None of the fields were provided.

    Raises:
        HTTPException: For validation errors or unexpected failures.
    """
    try:
        if not (data.name or data.surname or data.organization):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='None of the arguments were specified'
            )

        await UserCrud.update(
            session=session,
            record_id=auth_data['user'].id,
            name=data.name,
            surname=data.surname,
            organization=data.organization
        )
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(account_v1.post("/password", status_code=HTTP_204_NO_CONTENT), exclude_args=['data'])
async def change_password(
    auth_data: dict = Depends(access_token_auth),
    data: ChangePasswordRequest = Body(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Description
        Change the user password after verifying the current password and matching the new passwords.

    Args:
        auth_data (dict): Authenticated user data.
        data (ChangePasswordRequest): old_password, new_password1, new_password2.
        session (AsyncSession): Database session.

    Responses:
        204: Password updated successfully (no content).
        400: Old password incorrect or new passwords do not match.

    Raises:
        HTTPException: For validation errors or unexpected failures.
    """
    try:
        if data.new_password1 != data.new_password2:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='New passwords not equal'
            )
        if not verify_password(
                password=data.old_password,
                hashed_pass=auth_data['user'].password_hash):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Old password incorrect'
            )

        await UserCrud.update(
            session=session,
            record_id=auth_data['user'].id,
            password_hash=get_hashed_password(data.new_password1)
        )
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )
