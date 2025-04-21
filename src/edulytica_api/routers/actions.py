from uuid import UUID
from fastapi import APIRouter, Body, UploadFile, Depends, File
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.auth.auth_bearer import access_token_auth
from src.common.database.database import get_session
from src.common.utils.logger import api_logs


actions_router = APIRouter(prefix="/actions")


@api_logs(actions_router.post("/new_ticket"))
async def new_ticket(
    auth_data: dict = Depends(access_token_auth),
    file: UploadFile = File(...),
    event_id: UUID = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    pass


@api_logs(actions_router.get("/get_event_id"))
async def get_event_id(
    auth_data: dict = Depends(access_token_auth),
    event_name: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    pass


@api_logs(actions_router.get("/get_ticket"))
async def get_ticket(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    pass


@api_logs(actions_router.get("/get_ticket_file"))
async def get_ticket_file(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    pass


@api_logs(actions_router.get("/get_ticket_summary"))
async def get_ticket_summary(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    pass


@api_logs(actions_router.get("/get_ticket_result"))
async def get_ticket_result(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    pass


@api_logs(actions_router.post("/ticket_share"))
async def ticket_share(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    pass
