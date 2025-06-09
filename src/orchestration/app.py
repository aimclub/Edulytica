from contextlib import asynccontextmanager
import uvicorn
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from httpx import AsyncClient

from src.orchestration.routers.orchestrator_router import rt


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis_client = redis.from_url(
        "redis://edulytica_redis",
        encoding="utf-8",
        decode_responses=False
    )
    app.state.kafka_producer = AIOKafkaProducer(
        bootstrap_servers='kafka:9092'
    )
    app.state.http_client = AsyncClient()

    await app.state.redis_client.ping()
    await app.state.kafka_producer.start()

    yield

    await app.state.kafka_producer.stop()
    await app.state.redis_client.close()
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
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


app.include_router(rt)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=10001)
