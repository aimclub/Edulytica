"""
This module defines user account-related API endpoints for editing profile information,
changing passwords, and retrieving ticket history in a FastAPI application.

The endpoints are protected via JWT-based access token authentication and provide secure
ways for users to update their personal information or access their activity history.

Routes:
    POST /account/edit_profile: Updates the user's profile details (name, surname, organization).
    POST /account/change_password: Allows users to change their password after verifying the current one.
    GET /account/ticket_history: Returns the user's ticket history.
"""

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from src.common.auth.auth_bearer import access_token_auth
from src.common.auth.helpers.utils import verify_password, get_hashed_password
from src.common.database.crud.tickets_crud import TicketCrud
from src.common.database.crud.user_crud import UserCrud
from src.common.database.database import get_session
from src.common.utils.logger import api_logs
from src.edulytica_api.schemas.account_schemas import EditProfileRequest, ChangePasswordRequest


account_router = APIRouter(prefix="/account")


@api_logs(account_router.post("/edit_profile"))
async def edit_profile(
    auth_data: dict = Depends(access_token_auth),
    data: EditProfileRequest = Body(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Updates the authenticated user's profile information.

    Allows the user to modify one or more fields including their name, surname, and organization.
    At least one field must be specified.

    Args:
        auth_data (dict): Contains the authenticated user's data.
        data (EditProfileRequest): Pydantic-model, that contains name, surname and organization
        session (AsyncSession): Asynchronous database session.

    Raises:
        HTTPException: If no fields are provided or an internal error occurs.
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


@api_logs(account_router.post("/change_password"))
async def change_password(
    auth_data: dict = Depends(access_token_auth),
    data: ChangePasswordRequest = Body(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Changes the password for the authenticated user.

    Verifies that the provided old password is correct and the new passwords match
    before updating the stored password hash.

    Args:
        auth_data (dict): Contains the authenticated user's data.
        data (ChangePasswordRequest): Pydantic-model, that contain passwords
        session (AsyncSession): Asynchronous database session.

    Raises:
        HTTPException: If the old password is incorrect, the new passwords do not match,
        or if an internal error occurs.
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


@api_logs(account_router.get("/ticket_history"))
async def ticket_history(
    auth_data: dict = Depends(access_token_auth),
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieves the ticket history for the authenticated user.

    Returns all tickets associated with the user from the database.

    Args:
        auth_data (dict): Contains the authenticated user's data.
        session (AsyncSession): Asynchronous database session.

    Returns:
        dict: A message confirming the retrieval and a list of tickets.

    Raises:
        HTTPException: If an internal error occurs during data retrieval.
    """
    try:
        tickets = await TicketCrud.get_filtered_by_params(
            session=session,
            user_id=auth_data['user'].id
        )

        return {
            'detail': 'Ticket history found',
            'tickets': tickets
        }
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )
