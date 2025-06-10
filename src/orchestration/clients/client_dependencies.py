from fastapi import Request, Depends
from src.orchestration.clients.kafka_producer import KafkaProducer
from src.orchestration.clients.rag_client import RagClient
from src.orchestration.clients.state_manager import StateManager
from src.orchestration.orchestrator import Orchestrator


def get_kafka_producer(request: Request) -> KafkaProducer:
    return KafkaProducer(producer=request.app.state.kafka_producer)


def get_rag_client(request: Request) -> RagClient:
    return RagClient(
        http_client=request.app.state.http_client,
        base_url="http://edulytica_rag:10002"
    )


def get_state_manager(request: Request) -> StateManager:
    return StateManager(redis_client=request.app.state.redis_client)


def get_orchestrator(
    state_manager: StateManager = Depends(get_state_manager),
    kafka_producer: KafkaProducer = Depends(get_kafka_producer),
    rag_client: RagClient = Depends(get_rag_client)
) -> Orchestrator:
    return Orchestrator(
        state_manager=state_manager,
        kafka_producer=kafka_producer,
        rag_client=rag_client
    )
