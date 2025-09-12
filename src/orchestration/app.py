import asyncio
from contextlib import asynccontextmanager
import uvicorn
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from httpx import AsyncClient
from src.common.config import KAFKA_BOOTSTRAP_SERVERS, ORCHESTRATOR_PORT
from src.orchestration.clients.kafka_consumer import KafkaConsumer, KafkaNameConsumer
from src.common.config import KAFKA_BOOTSTRAP_SERVERS, ORCHESTRATOR_PORT, RAG_PORT
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
    kafka_consumer_result = AIOKafkaConsumer(
        "llm_tasks.result",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="orchestrator_results_group",
        auto_offset_reset='earliest'
    )
    kafka_consumer_names = AIOKafkaConsumer(
        "llm_name.result",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="orchestrator_names_group",
        auto_offset_reset='earliest'
    )

    http_client = AsyncClient()

    try:
        await redis_client.ping()
        await kafka_producer_client.start()
        await kafka_consumer_result.start()
        await kafka_consumer_names.start()

        state_manager = StateManager(redis_client=redis_client)
        kafka_producer = KafkaProducer(producer=kafka_producer_client)
        rag_client = RagClient(http_client=http_client, base_url="http://edulytica_rag:10002")
        result_consumer = KafkaConsumer(
            consumer=kafka_consumer_result,
            state_manager=state_manager,
            kafka_producer=kafka_producer,
            rag_client=rag_client
        )
        names_consumer = KafkaNameConsumer(
            consumer=kafka_consumer_names,
            state_manager=state_manager,
            kafka_producer=kafka_producer,
            rag_client=rag_client
        )

        app.state.redis_client = redis_client
        app.state.state_manager = state_manager
        app.state.kafka_producer = kafka_producer_client
        app.state.rag_client = rag_client
        app.state.http_client = http_client

        task_results = asyncio.create_task(result_consumer.consume())
        task_names = asyncio.create_task(names_consumer.consume())
        app.state._consumer_tasks = [task_results, task_names]

        yield
    finally:
        tasks = getattr(app.state, "_consumer_tasks", [])
        for t in tasks:
            if t and not t.done():
                t.cancel()
        for t in tasks:
            if t:
                try:
                    await t
                except asyncio.CancelledError:
                    pass

        await kafka_consumer_names.stop()
        await kafka_consumer_results.stop()
        await kafka_producer_client.stop()
        await redis_client.close()
        await http_client.aclose()

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


app.include_router(rt)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=ORCHESTRATOR_PORT)
