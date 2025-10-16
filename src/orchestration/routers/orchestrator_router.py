import uuid
from fastapi import APIRouter, Body, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST
from src.common.database.crud.tickets_crud import TicketCrud
from src.common.database.database import get_session
from src.orchestration.clients.client_dependencies import get_state_manager, get_kafka_producer, \
    get_rag_client
from src.orchestration.clients.kafka_producer import KafkaProducer
from src.orchestration.clients.rag_client import RagClient
from src.orchestration.clients.state_manager import StateManager
from src.orchestration.orchestrator import Orchestrator


rt = APIRouter(prefix='/orchestrate')


@rt.post('/run_ticket')
async def run_ticket_handler(
        background_tasks: BackgroundTasks,
        ticket_id: uuid.UUID = Body(...),
        mega_task_id: str = Body(...),
        document_text: str = Body(...),
        state_manager: StateManager = Depends(get_state_manager),
        kafka_producer: KafkaProducer = Depends(get_kafka_producer),
        rag_client: RagClient = Depends(get_rag_client),
        session: AsyncSession = Depends(get_session)
):
    try:
        event_name = await TicketCrud.get_event_name_for_ticket(session=session, ticket_id=ticket_id)

        orchestrator = Orchestrator(
            state_manager=state_manager,
            kafka_producer=kafka_producer,
            rag_client=rag_client,
            mega_task_id=mega_task_id,
            event_name=event_name
        )

        background_tasks.add_task(
            orchestrator.run_pipeline,
            ticket_id=ticket_id,
            document_text=document_text
        )
    except ValueError as _ve:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=f"{_ve}"
        )
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f"500 ERR: {_e}"
        )


@rt.delete('/tickets/{ticket_id}')
async def delete_ticket(
    ticket_id: uuid.UUID,
    state_manager: StateManager = Depends(get_state_manager),
):
    try:
        await state_manager.delete_ticket(ticket_id=ticket_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f"500 ERR: {_e}"
        )
