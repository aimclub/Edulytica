import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.rag.routers.rag import rag_router
from src.common.config import RAG_PORT
from src.rag.seeding import seed_initial_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(seed_initial_data())
    yield


app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://10.22.8.250",
    "http://10.22.8.250:13000"
]

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
)


app.include_router(rag_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=RAG_PORT)
