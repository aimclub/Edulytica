from fastapi import Request

from edulytica.common.config import RAG_PORT
from edulytica.orchestration.clients.kafka_producer import KafkaProducer
from edulytica.orchestration.clients.rag_client import RagClient
from edulytica.orchestration.clients.state_manager import StateManager


def get_kafka_producer(request: Request) -> KafkaProducer:
    return KafkaProducer(producer=request.app.state.kafka_producer)


def get_rag_client(request: Request) -> RagClient:
    return RagClient(
        http_client=request.app.state.http_client,
        base_url=f"http://edulytica_rag:{RAG_PORT}"
    )


def get_state_manager(request: Request) -> StateManager:
    return StateManager(redis_client=request.app.state.redis_client)
