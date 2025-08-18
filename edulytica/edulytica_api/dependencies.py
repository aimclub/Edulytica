from fastapi import Request
from httpx import AsyncClient


def get_http_client(request: Request) -> AsyncClient:
    return request.app.state.http_client
