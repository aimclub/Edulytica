from fastapi import Request
from src.orchestration.clients.kafka_producer import KafkaProducer
from src.orchestration.clients.rag_client import RagClient
from src.orchestration.clients.state_manager import StateManager


# client = Depends(get_client)


def get_kafka_producer(request: Request) -> KafkaProducer:
    return KafkaProducer(producer=request.app.state.kafka_producer)


def get_rag_client(request: Request) -> RagClient:
    return RagClient(
        http_client=request.app.state.http_client,
        base_url="http://edulytica_rag:10002"
    )


def get_state_manager(request: Request) -> StateManager:
    return StateManager(redis_client=request.app.state.redis_client)
