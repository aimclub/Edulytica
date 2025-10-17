"""
Description
    Orchestrator API for starting ticket processing and clearing ticket state.
    The orchestrator composes StateManager, KafkaProducer, and RagClient and
    runs the document-processing pipeline in a background task.

Routes:
    POST   /run_ticket      — Schedule pipeline execution for a ticket.
    DELETE /tickets/{id}    — Remove ticket state from the orchestrator.
"""

import uuid
from fastapi import APIRouter, Body, BackgroundTasks, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT, \
    HTTP_202_ACCEPTED
from src.common.database.crud.ticket_crud import TicketCrud
from src.common.database.database import get_session
from src.common.utils.logger import api_logs
from src.orchestration.clients.client_dependencies import get_state_manager, get_kafka_producer, \
    get_rag_client
from src.orchestration.clients.kafka_producer import KafkaProducer
from src.orchestration.clients.rag_client import RagClient
from src.orchestration.clients.state_manager import StateManager
from src.orchestration.orchestrator import Orchestrator


orchestrator_v1 = APIRouter(prefix='/api/orchestrator/v1', tags=['orchestrator'])


@api_logs(
    orchestrator_v1.post('/run_ticket', status_code=HTTP_202_ACCEPTED),
    exclude_args=['background_tasks', 'state_manager', 'kafka_producer', 'rag_client', 'document_text']
)
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
    """
    Description
        Schedule the orchestrator pipeline for the given ticket and document text.
        Resolves the event name for the ticket, initializes the Orchestrator, and enqueues
        a background task to run the pipeline.

    Args:
        background_tasks (BackgroundTasks): FastAPI background tasks manager.
        ticket_id (UUID): Target ticket identifier.
        mega_task_id (str): Pipeline selector for the orchestrator.
        document_text (str): Normalized text extracted from the uploaded document.
        state_manager (StateManager): Orchestrator state manager instance.
        kafka_producer (KafkaProducer): Producer used for orchestrator messaging.
        rag_client (RagClient): Client for RAG interactions during pipeline execution.
        session (AsyncSession): Database session (used to resolve event name).

    Responses:
        202: Pipeline execution scheduled (work enqueued).
        400: Invalid input (e.g., unsupported mega_task_id) or ticket/event lookup error.
        500: Unexpected server error.

    Raises:
        HTTPException: On validation failures, lookup errors, or internal exceptions.
    """
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

        return Response(status_code=HTTP_202_ACCEPTED)
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


@api_logs(orchestrator_v1.delete('/tickets/{ticket_id}', status_code=HTTP_204_NO_CONTENT), exclude_args=['state_manager'])
async def delete_ticket(
    ticket_id: uuid.UUID,
    state_manager: StateManager = Depends(get_state_manager),
):
    """
    Description
        Remove all orchestrator-managed state for the specified ticket (idempotent).
        This does not delete the ticket from the database; it clears runtime state only.

    Args:
        ticket_id (UUID): Target ticket identifier.
        state_manager (StateManager): Orchestrator state manager instance.

    Responses:
        204: Ticket state removed (no content).

    Raises:
        HTTPException: On unexpected errors.
    """
    try:
        await state_manager.delete_ticket(ticket_id=ticket_id)
        return Response(status_code=HTTP_204_NO_CONTENT)
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f"500 ERR: {_e}"
        )
