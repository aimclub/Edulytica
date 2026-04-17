from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient
from src.common.config import API_PORT, ALLOWED_ORIGINS
from src.edulytica_api.api.v1 import routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    http_client = AsyncClient()

    try:
        app.state.http_client = http_client

        yield
    finally:
        await http_client.aclose()


app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

for origin in ALLOWED_ORIGINS:
    if origin not in origins:
        origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "OPTIONS",
        "DELETE",
        "PATCH",
        "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization"],
    expose_headers=["Content-Disposition", "Content-Type"]
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {"status": "ok"}


for rt in routers:
    app.include_router(rt)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)
