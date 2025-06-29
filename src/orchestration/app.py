import asyncio
from contextlib import asynccontextmanager
import uvicorn
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from httpx import AsyncClient
from src.common.config import KAFKA_BOOTSTRAP_SERVERS, ORCHESTRATOR_PORT
from src.orchestration.clients.kafka_consumer import KafkaConsumer
from src.orchestration.clients.kafka_producer import KafkaProducer
from src.orchestration.clients.rag_client import RagClient
from src.orchestration.clients.state_manager import StateManager
from src.orchestration.routers.orchestrator_router import rt


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url(
        "redis://edulytica_redis",
        encoding="utf-8",
        decode_responses=False
    )
    kafka_producer_client = AIOKafkaProducer(
        bootstrap_servers='kafka:9092'
    )
    kafka_consumer_client = AIOKafkaConsumer(
        "llm_tasks.result",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="orchestrator_results_group",
        auto_offset_reset='earliest'
    )
    http_client = AsyncClient()

    try:
        await redis_client.ping()
        await kafka_producer_client.start()
        await kafka_consumer_client.start()

        state_manager = StateManager(redis_client=redis_client)
        kafka_producer_client = KafkaProducer(producer=kafka_producer_client)
        rag_client = RagClient(http_client=http_client, base_url="http://edulytica_rag:10002")

        kafka_consumer = KafkaConsumer(
            consumer=kafka_consumer_client,
            state_manager=state_manager,
            kafka_producer=kafka_producer_client,
            rag_client=rag_client
        )

        app.state.state_manager = state_manager
        app.state.rag_client = rag_client
        app.state.http_client = http_client

        consumer_task = asyncio.create_task(kafka_consumer.consume())

        yield
    finally:
        if 'consumer_task' in locals() and not consumer_task.done():
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                print("Consumer task successfully cancelled.")

        await kafka_consumer_client.stop()
        await kafka_producer_client.stop()
        await redis_client.close()
        await http_client.aclose()

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
    uvicorn.run(app, host="0.0.0.0", port=ORCHESTRATOR_PORT)
