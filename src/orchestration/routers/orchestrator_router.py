from fastapi import APIRouter


rt = APIRouter(prefix='orchestrate')


@rt.get('ping')
async def ping_ep():
    return {'detail': 'pong'}
