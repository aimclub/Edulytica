"""
This module defines API endpoints for ticket and document-related actions in a FastAPI application.

It enables users to upload documents, create and manage tickets, download ticket-related files such as
summaries and reports, and retrieve event identifiers. The system supports both standard and custom events,
and performs document processing through background tasks. All routes are protected with JWT-based access
token authentication.

Routes:
    POST /actions/new_ticket: Uploads a document and creates a new ticket for an event.
    GET /actions/get_event_id: Retrieves the event ID by event name.
    GET /actions/get_ticket: Retrieves a ticket if it belongs to the user or was shared.
    GET /actions/get_ticket_file: Downloads the original file attached to the ticket.
    GET /actions/get_ticket_summary: Downloads the LLM-generated document summary.
    GET /actions/get_ticket_result: Downloads the LLM-generated result or report.
    POST /actions/ticket_share: Toggles the shared status of a ticket.
"""

import os
import uuid
from io import BytesIO
from pathlib import Path
from uuid import UUID
import httpx
from fastapi import APIRouter, Body, UploadFile, Depends, File, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST, HTTP_503_SERVICE_UNAVAILABLE
from src.common.auth.auth_bearer import access_token_auth
from src.common.config import ORCHESTRATOR_PORT, RAG_PORT
from src.common.database.crud.document_report_crud import DocumentReportCrud
from src.common.database.crud.document_summary_crud import DocumentSummaryCrud
from src.common.database.crud.event_crud import EventCrud
from src.common.database.crud.custom_event_crud import CustomEventCrud
from src.common.database.crud.document_crud import DocumentCrud
from src.common.database.crud.ticket_status_crud import TicketStatusCrud
from src.common.database.crud.ticket_type_crud import TicketTypeCrud
from src.common.database.crud.tickets_crud import TicketCrud
from src.common.database.database import get_session
from src.common.utils.chroma_utils import is_valid_chroma_collection_name
from src.common.utils.default_enums import TicketStatusDefault, TicketTypeDefault
from src.common.utils.logger import api_logs
from src.edulytica_api.dependencies import get_http_client
from src.edulytica_api.parser.Parser import get_structural_paragraphs, fast_parse_text

actions_router = APIRouter(prefix="/actions")
ROOT_DIR = Path(__file__).resolve().parents[3]


@api_logs(actions_router.post("/new_ticket"))
async def new_ticket(
    auth_data: dict = Depends(access_token_auth),
    file: UploadFile = File(...),
    event_id: UUID = Body(...),
    mega_task_id: str = Body(...),
    session: AsyncSession = Depends(get_session),
    http_client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Creates a new ticket by uploading a document and associating it with an event.

    Validates the event and file type, stores the file, creates a document record,
    and initializes a ticket. Then queues a background task for LLM analysis.

    Args:
        auth_data (dict): Authenticated user data.
        file (UploadFile): Uploaded PDF or DOCX file.
        event_id (UUID): ID of the associated event (standard or custom).
        mega_task_id (str): ID of mega task
        session (AsyncSession): Database session.
        http_client (AsyncClient): Async HTTP Client

    Returns:
        dict: Success message and ticket ID.

    Raises:
        HTTPException: For invalid event ID, unsupported file type, or internal errors.
    """
    try:
        if mega_task_id not in ["1", "2"]:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail=f"Unknown megatask id {mega_task_id}"
            )

        custom_event = None
        event = await EventCrud.get_by_id(session=session, record_id=event_id)
        if not event:
            custom_event = await CustomEventCrud.get_by_id(session=session, record_id=event_id)

        if not (event or custom_event):
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Incorrect event id')

        if file.content_type not in [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]:
            raise HTTPException(status_code=400, detail='Invalid file type, only PDF or DOCX')

        file_extension = (file.filename or '').rsplit('.', 1)[-1].lower()
        while True:
            file_id = uuid.uuid4()
            if not await DocumentCrud.get_by_id(session=session, record_id=file_id):
                break

        file_dir = os.path.join(ROOT_DIR, 'app_files', 'document', f'{auth_data["user"].id}')
        os.makedirs(file_dir, exist_ok=True)
        saved_file_path = os.path.join(file_dir, f'{file_id}.{file_extension}')

        file_path = os.path.join(
            'app_files', 'document', f'{auth_data["user"].id}', f'{file_id}.{file_extension}'
        )
        with open(saved_file_path, 'wb') as f:
            f.write(await file.read())

        try:
            with open(saved_file_path, 'rb') as f:
                parsed_data = fast_parse_text(f, filename=file.filename)

            document_text = parsed_data
            if not document_text:
                raise ValueError("Parser could not extract text from the document.")

        except Exception as _e:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse the document: {_e}")

        await DocumentCrud.create(
            session=session, user_id=auth_data['user'].id, file_path=file_path, id=file_id
        )

        ticket_status = await TicketStatusCrud.get_filtered_by_params(
            session=session, name=TicketStatusDefault.CREATED.value
        )
        ticket_type = await TicketTypeCrud.get_filtered_by_params(
            session=session, name=TicketTypeDefault.ACHIEVABILITY.value
        )

        ticket_data = {
            'session': session,
            'user_id': auth_data['user'].id,
            'ticket_status_id': ticket_status[0].id,
            'ticket_type_id': ticket_type[0].id,
            'document_id': file_id
        }
        if event:
            ticket_data['event_id'] = event.id
        elif custom_event:
            ticket_data['custom_event_id'] = custom_event.id
        ticket = await TicketCrud.create(**ticket_data)

        orchestrator_payload = {
            "ticket_id": str(ticket.id),
            "mega_task_id": mega_task_id,
            "document_text": document_text
        }

        try:
            response = await http_client.post(f'http://edulytica_orchestration:{ORCHESTRATOR_PORT}'
                                              f'/orchestrate/run_ticket',
                                              json=orchestrator_payload, timeout=30.0)
            response.raise_for_status()
        except httpx.RequestError as _re:
            raise HTTPException(
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Orchestration service is unavailable {_re}"
            )
        except httpx.HTTPStatusError as _hse:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Orchestrator failed to start task: {_hse.response.text}"
            )

        return JSONResponse(
            status_code=202,
            content={
                'detail': 'Ticket has been created and sent for processing',
                'ticket_id': str(
                    ticket.id)})
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')


@api_logs(actions_router.post("/parse_file_text"))
async def parse_file_text(
        auth_data: dict = Depends(access_token_auth),
        file: UploadFile = File(...),
):
    """
    Extracts text content from an uploaded PDF or DOCX file.

    This is a universal endpoint that can parse any supported file format
    and return its text content. Useful for extracting text from original documents,
    summaries, reports, or any other file type that may be added in the future.

    Args:
        auth_data (dict): Authenticated user data.
        file (UploadFile): Uploaded PDF or DOCX file to parse.

    Returns:
        dict: Extracted text content and file metadata.

    Raises:
        HTTPException: For unsupported file type or text extraction errors.
    """
    try:
        if file.content_type not in [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        ]:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Invalid file type, only PDF or DOCX supported'
            )

        try:
            file_content = await file.read()

            if file.content_type == 'text/plain':
                try:
                    document_text = file_content.decode('utf-8')
                except UnicodeDecodeError:
                    raise ValueError(
                        "Failed to decode TXT file. Please ensure it is UTF-8 encoded.")
            else:
                file_like = BytesIO(file_content)
                document_text = fast_parse_text(file_like, filename=file.filename)

            if not document_text:
                raise ValueError("Parser could not extract text from the document.")

        except Exception as e:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse the document: {e}"
            )

        return {'detail': 'Text was parsed', 'text': document_text}

    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(actions_router.post('/add_custom_event'))
async def add_custom_event(
    auth_data: dict = Depends(access_token_auth),
    event_name: str = Body(...),
    description: str = Body(...),
    session: AsyncSession = Depends(get_session),
    http_client: httpx.AsyncClient = Depends(get_http_client)
):
    try:
        if is_valid_chroma_collection_name(event_name):
            event = await EventCrud.get_filtered_by_params(session=session, name=event_name)
            custom_event = await CustomEventCrud.get_filtered_by_params(session=session, name=event_name)

            if event or custom_event:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail=f'Event with name {event_name} already exists.'
                )

            try:
                rag_payload = {
                    "text": description,
                    "event_name": event_name
                }
                response = await http_client.post(f'http://edulytica_rag:{RAG_PORT}'
                                                  f'/rag/upload_text',
                                                  json=rag_payload, timeout=30.0)
                response.raise_for_status()
                await CustomEventCrud.create(
                    session=session,
                    name=event_name,
                    user_id=auth_data['user'].id
                )
            except httpx.RequestError as _re:
                raise HTTPException(
                    status_code=HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"RAG service is unavailable {_re}"
                )
        else:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Invalid event name specified. Only latin characters, numbers, and ._- are allowed.')
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')


@api_logs(actions_router.get('/get_ticket_status'))
async def get_ticket_status(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Query(...),
    session: AsyncSession = Depends(get_session)
):
    try:
        ticket = await TicketCrud.get_by_id(session=session, record_id=ticket_id)
        ticket_status = await TicketStatusCrud.get_by_id(session=session, record_id=ticket.ticket_status_id)

        return {'detail': 'Ticket status was found', 'status': ticket_status.name}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')


@api_logs(actions_router.get("/get_events"))
async def get_events(
    auth_data: dict = Depends(access_token_auth),
    session: AsyncSession = Depends(get_session),
):
    """
    Retrieves a list of all events available to the user.
    Includes both standard and custom events.
    Args:
        auth_data (dict): Authenticated user data.
        session (AsyncSession): Database session.
    Returns:
        dict: List of events with their IDs and names.
    Raises:
        HTTPException: If an internal server error occurs.
    """
    try:
        standard_events = await EventCrud.get_all(session=session)
        standard_events_list = [
            {"id": event.id, "name": event.name, "type": "standard"}
            for event in standard_events
        ]

        custom_events = await CustomEventCrud.get_filtered_by_params(
            session=session, user_id=auth_data["user"].id
        )
        custom_events_list = [
            {"id": event.id, "name": event.name, "type": "custom"}
            for event in custom_events
        ]

        all_events = standard_events_list + custom_events_list

        return {"detail": "Events were found", "events": all_events}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f"500 ERR: {_e}"
        )


@api_logs(actions_router.get("/get_event_id"))
async def get_event_id(
    auth_data: dict = Depends(access_token_auth),
    event_name: str = Query(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieves the event ID by event name.

    Searches for both standard and custom events created by the user.

    Args:
        auth_data (dict): Authenticated user data.
        event_name (str): The name of the event to look up.
        session (AsyncSession): Database session.

    Returns:
        dict: Event ID if found.

    Raises:
        HTTPException: If the event does not exist or internal error occurs.
    """
    try:
        event = await EventCrud.get_filtered_by_params(session=session, name=event_name)
        if not event:
            event = await CustomEventCrud.get_filtered_by_params(
                session=session, name=event_name, user_id=auth_data['user'].id
            )

        if not event:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Event doesn\'t exist')

        return {'detail': 'Event was found', 'event_id': event[0].id}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')


@api_logs(actions_router.get("/get_ticket"))
async def get_ticket(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Query(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieves a ticket if it belongs to the user or was shared.

    Args:
        auth_data (dict): Authenticated user data.
        ticket_id (UUID): Ticket UUID.
        session (AsyncSession): Database session.

    Returns:
        dict: Ticket data.

    Raises:
        HTTPException: If ticket not found or unauthorized access.
    """
    try:
        ticket = await TicketCrud.get_ticket_by_id_or_shared(
            session=session, ticket_id=ticket_id, user_id=auth_data['user'].id
        )

        if not ticket:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                                detail='Ticket doesn\'t exist or you\'re not ticket creator')

        return {'detail': 'Ticket was found', 'ticket': ticket}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')


@api_logs(actions_router.get("/get_ticket_file"))
async def get_ticket_file(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Query(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Downloads the original file attached to a ticket.

    Args:
        auth_data (dict): Authenticated user data.
        ticket_id (UUID): Ticket UUID.
        session (AsyncSession): Database session.

    Returns:
        FileResponse: The original uploaded file.

    Raises:
        HTTPException: If the ticket or file is not found.
    """
    try:
        ticket = await TicketCrud.get_ticket_by_id_or_shared(
            session=session, ticket_id=ticket_id, user_id=auth_data['user'].id
        )
        if not ticket:
            raise HTTPException(status_code=400, detail='Ticket doesn\'t exist')

        document = await DocumentCrud.get_by_id(session=session, record_id=ticket.document_id)
        if not document:
            raise HTTPException(status_code=400, detail='File not found in Database')

        file_path = ROOT_DIR / document.file_path

        if not file_path.exists():
            raise HTTPException(status_code=400, detail='File not found in storage')

        return FileResponse(
            path=str(file_path),
            media_type='application/octet-stream',
            filename=file_path.name)
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')


@api_logs(actions_router.get("/get_ticket_summary"))
async def get_ticket_summary(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Query(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Downloads the LLM-generated document summary for a ticket.

    Args:
        auth_data (dict): Authenticated user data.
        ticket_id (UUID): Ticket UUID.
        session (AsyncSession): Database session.

    Returns:
        FileResponse: The summary file.

    Raises:
        HTTPException: If the summary or ticket does not exist.
    """
    try:
        ticket = await TicketCrud.get_ticket_by_id_or_shared(
            session=session, ticket_id=ticket_id, user_id=auth_data['user'].id
        )
        if not ticket:
            raise HTTPException(status_code=400, detail='Ticket doesn\'t exist')

        document_summary = await DocumentSummaryCrud.get_by_id(
            session=session, record_id=ticket.document_summary_id
        )
        if not document_summary:
            raise HTTPException(status_code=400, detail='Ticket summary not found')

        file_path = ROOT_DIR / document_summary.file_path
        if not file_path.exists():
            raise HTTPException(status_code=400, detail='Ticket summary not found')

        return FileResponse(
            path=str(file_path),
            media_type='application/octet-stream',
            filename=file_path.name)
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')


@api_logs(actions_router.get("/get_ticket_result"))
async def get_ticket_result(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Query(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Downloads the LLM-generated result file for a ticket.

    Args:
        auth_data (dict): Authenticated user data.
        ticket_id (UUID): Ticket UUID.
        session (AsyncSession): Database session.

    Returns:
        FileResponse: The result file.

    Raises:
        HTTPException: If the report is not found or ticket doesn't exist.
    """
    try:
        ticket = await TicketCrud.get_ticket_by_id_or_shared(
            session=session, ticket_id=ticket_id, user_id=auth_data['user'].id
        )
        if not ticket:
            raise HTTPException(status_code=400, detail='Ticket doesn\'t exist')

        document_report = await DocumentReportCrud.get_by_id(
            session=session, record_id=ticket.document_report_id
        )

        if not document_report:
            raise HTTPException(
                status_code=400,
                detail=f'Ticket result not found, document report not found in Database')

        file_path = ROOT_DIR / document_report.file_path

        if not file_path.exists():
            raise HTTPException(
                status_code=400,
                detail='Ticket result not found, document report not found in storage')

        return FileResponse(
            path=str(file_path),
            media_type='application/octet-stream',
            filename=file_path.name)
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')


@api_logs(actions_router.post("/ticket_share"))
async def ticket_share(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    """
    Toggles the shared status of a ticket owned by the user.

    Args:
        auth_data (dict): Authenticated user data.
        ticket_id (UUID): Ticket UUID.
        session (AsyncSession): Database session.

    Returns:
        dict: Message confirming status change.

    Raises:
        HTTPException: If the user does not own the ticket, or it does not exist.
    """
    try:
        ticket = await TicketCrud.get_filtered_by_params(
            session=session, user_id=auth_data['user'].id, id=ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='You aren\'t ticket owner or ticket doesn\'t exist'
            )

        await TicketCrud.update(
            session=session, record_id=ticket_id, shared=(not ticket.shared)
        )

        return {'detail': 'Status has been changed'}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')
