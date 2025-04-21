from typing import Optional
from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.auth.auth_bearer import access_token_auth
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
    pass


@api_logs(account_router.post("/change_password"))
async def change_password(
    auth_data: dict = Depends(access_token_auth),
    old_password: str = Body(...),
    new_password1: str = Body(...),
    new_password2: str = Body(...),
    session: AsyncSession = Depends(get_session)
):
    pass


@api_logs(account_router.get("/ticket_history"))
async def ticket_history(
    auth_data: dict = Depends(access_token_auth),
    session: AsyncSession = Depends(get_session)
):
    pass
