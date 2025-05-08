from fastapi import APIRouter, Body
from src.common.utils.logger import api_logs


rag_router = APIRouter(prefix="/rag")


@api_logs(rag_router.post('/upload_text'))
async def upload_text_handler(
        text: str = Body(..., embed=True)
):
    pass


@api_logs(rag_router.post('/get_result'))
async def get_result_handler(
        text: str,
        event_name: str,
        prompt: str
):
    # return str
    pass
