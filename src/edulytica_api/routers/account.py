from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from src.common.auth.auth_bearer import access_token_auth
from src.common.auth.helpers.utils import verify_password, get_hashed_password
from src.common.database.crud.tickets_crud import TicketCrud
from src.common.database.crud.user_crud import UserCrud
from src.common.database.database import get_session
from src.common.utils.logger import api_logs


account_router = APIRouter(prefix="/account")


@api_logs(account_router.post("/edit_profile"))
async def edit_profile(
    auth_data: dict = Depends(access_token_auth),
    name: Optional[str] = Body(None),
    surname: Optional[str] = Body(None),
    organization: Optional[str] = Body(None),
    session: AsyncSession = Depends(get_session)
):
    try:
        if not (name or surname or organization):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='None of the arguments were specified'
            )

        await UserCrud.update(
            session=session,
            record_id=auth_data['user'].id,
            name=name,
            surname=surname,
            organization=organization
        )
    except Exception as _e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(account_router.post("/change_password"))
async def change_password(
    auth_data: dict = Depends(access_token_auth),
    old_password: str = Body(...),
    new_password1: str = Body(...),
    new_password2: str = Body(...),
    session: AsyncSession = Depends(get_session)
):
    try:
        if not verify_password(password=old_password, hashed_pass=auth_data['user'].password_hash):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Old password incorrect'
            )
        if new_password1 != new_password2:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='New passwords not equal'
            )

        await UserCrud.update(
            session=session,
            record_id=auth_data['user'].id,
            password_hash=get_hashed_password(new_password1)
        )
    except Exception as _e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(account_router.get("/ticket_history"))
async def ticket_history(
    auth_data: dict = Depends(access_token_auth),
    session: AsyncSession = Depends(get_session)
):
    try:
        tickets = await TicketCrud.get_filtered_by_params(
            session=session,
            user_id=auth_data['user'].id
        )

        return {
            'detail': 'Ticket history found',
            'tickets': tickets
        }
    except Exception as _e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )
