from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.auth.auth_bearer import refresh_token_auth, access_token_auth
from src.common.database.database import get_session
from src.common.utils.logger import api_logs


auth_router = APIRouter()


@api_logs(auth_router.post('/registration'))
async def registration_handler(
        login: str = Body(...),
        email: str = Body(...),
        password1: str = Body(...),
        password2: str = Body(...),
        session: AsyncSession = Depends(get_session)
):
    pass


@api_logs(auth_router.post('/check_code'))
async def check_code_handler(
        code: str = Body(..., embed=True),
        session: AsyncSession = Depends(get_session)
):
    pass


@api_logs(auth_router.post('login'))
async def login_handler(
        login: str = Body(...),
        password: str = Body(...),
        session: AsyncSession = Depends(get_session)
):
    pass


@api_logs(auth_router.get('/get_access'))
async def get_access_handler(
        refresh_token: dict = Depends(refresh_token_auth),
        session: AsyncSession = Depends(get_session)
):
    pass


@api_logs(auth_router.get('/logout'))
async def logout_handler(
        access_token: dict = Depends(access_token_auth),
        session: AsyncSession = Depends(get_session)
):
    pass
