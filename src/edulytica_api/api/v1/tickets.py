import httpx
import os

from io import BytesIO
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, UploadFile, File, Body, HTTPException, Query, Path as FPath
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_503_SERVICE_UNAVAILABLE, HTTP_500_INTERNAL_SERVER_ERROR, \
    HTTP_403_FORBIDDEN
from src.common.auth.auth_bearer import access_token_auth
from src.common.config import ORCHESTRATOR_PORT
from src.common.database.crud import EventCrud, CustomEventCrud, DocumentCrud, TicketStatusCrud, TicketTypeCrud, \
    TicketCrud
from src.common.database.database import get_session
from src.common.utils.default_enums import TicketStatusDefault, TicketTypeDefault
from src.common.utils.logger import api_logs
from src.edulytica_api.dependencies import get_http_client
from src.edulytica_api.parser.Parser import fast_parse_text


tickets_v1 = APIRouter(prefix="/api/tickets/v1", tags=["tickets"])
ROOT_DIR = Path(__file__).resolve().parents[4]


@api_logs(tickets_v1.get(""))
async def list_tickets(
    auth_data: dict = Depends(access_token_auth),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1),
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieves the ticket history for the authenticated user.

    Returns all tickets associated with the user from the database.

    Args:
        auth_data (dict): Contains the authenticated user's data.
        page (int): Page number for pagination (default is 1).
        size (int): Number of tickets per page for pagination (default is 20).
        session (AsyncSession): Asynchronous database session.

    Returns:
        dict: A message confirming the retrieval and a list of tickets.

    Raises:
        HTTPException: If an internal error occurs during data retrieval.
    """
    try:
        tickets = await TicketCrud.get_paginated_user_tickets(
            session=session,
            user_id=auth_data['user'].id,
            skip=(size * (page - 1)),
            limit=size
        )

        return {
            'detail': 'Ticket history found',
            'tickets': tickets
        }
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(tickets_v1.post(""), exclude_args=['file', 'http_client'])
async def create_ticket(
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
            file_id = uuid4()
            if not await DocumentCrud.get_by_id(session=session, record_id=file_id):
                break

        file_dir = os.path.join(ROOT_DIR, 'app_files', 'document', f'{auth_data["user"].id}')
        os.makedirs(file_dir, exist_ok=True)
        saved_file_path = os.path.join(file_dir, f'{file_id}.{file_extension}')

        file_path = os.path.join(
            'app_files', 'document', f'{auth_data["user"].id}', f'{file_id}.{file_extension}'
        )

        file_content = await file.read()

        with open(saved_file_path, 'wb') as f:
            f.write(file_content)

        try:
            file_stream = BytesIO(file_content)
            document_text = fast_parse_text(file_stream, filename=file.filename)

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
            'name': file.filename if file.filename else 'New ticket',
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
                                              f'/api/orchestrator/v1//run_ticket',
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


@api_logs(tickets_v1.get("/{ticket_id}"))
async def get_ticket(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = FPath(...),
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


@api_logs(tickets_v1.get('/{ticket_id}/status'))
async def get_ticket_status(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = FPath(...),
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


@api_logs(tickets_v1.patch("/{ticket_id}/name"))
async def edit_ticket_name(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = FPath(...),
    name: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    try:
        ticket = await TicketCrud.get_by_id(session, record_id=ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f'Ticket not found')

        if ticket.user_id != auth_data['user'].id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="You're not ticket creator"
            )

        if len(name) > 60:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Ticket name too long, maximum: 60 characters'
            )

        await TicketCrud.update(session, record_id=ticket_id, name=name)
        return {'detail': 'Ticket name has been updated'}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')


@api_logs(tickets_v1.delete("/{ticket_id}"), exclude_args=['http_client'])
async def delete_ticket(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = FPath(...),
    session: AsyncSession = Depends(get_session),
    http_client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Deletes a ticket owned by the user.

    Args:
        auth_data (dict): Authenticated user data.
        ticket_id (UUID): Ticket UUID.
        session (AsyncSession): Database session.
        http_client (AsyncClient): Async HTTP Client.

    Returns:
        dict: Message confirming deletion.

    Raises:
        HTTPException: If the user does not own the ticket, or it does not exist.
    """
    try:
        tickets = await TicketCrud.get_filtered_by_params(
            session=session, user_id=auth_data['user'].id, id=ticket_id
        )

        if not tickets or len(tickets) == 0:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='You aren\'t ticket owner or ticket doesn\'t exist'
            )

        try:
            response = await http_client.delete(
                f"http://edulytica_orchestration:{ORCHESTRATOR_PORT}/api/orchestrator/v1/tickets/{ticket_id}",
                timeout=30.0
            )
            response.raise_for_status()
        except httpx.RequestError as _re:
            raise HTTPException(
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Orchestration service is unavailable {_re}"
            )
        except httpx.HTTPStatusError as _hse:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Orchestrator failed to delete ticket: {_hse.response.text}"
            )

        await TicketCrud.delete(session, record_id=ticket_id)

        return {'detail': 'Ticket was deleted'}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')


@api_logs(tickets_v1.post("/{ticket_id}/share"))
async def ticket_share(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = FPath(...),
    session: AsyncSession = Depends(get_session),
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
            session=session, record_id=ticket_id, shared=(not ticket[0].shared)
        )

        return {'detail': 'Share status has been changed'}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')
