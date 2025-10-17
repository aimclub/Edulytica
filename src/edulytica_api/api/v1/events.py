"""
Description
    Events API for listing available events (standard and user-defined), getting an event ID by name,
    and creating a custom event backed by a RAG service. Requires a valid JWT access token.

Routes:
    GET  /         — List standard and user custom events available to the user.
    GET  /by_name  — Get event ID by name (checks standard and user custom).
    POST /         — Create a custom event and upload its description to RAG.
"""

import httpx

from fastapi import APIRouter, Depends, Body, HTTPException, Query
from networkx.algorithms.tree import random_spanning_tree
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_503_SERVICE_UNAVAILABLE, HTTP_500_INTERNAL_SERVER_ERROR, \
    HTTP_200_OK, HTTP_201_CREATED

from src.common.auth.auth_bearer import access_token_auth
from src.common.config import RAG_PORT
from src.common.database.crud import EventCrud, CustomEventCrud
from src.common.database.database import get_session
from src.common.utils.chroma_utils import is_valid_chroma_collection_name
from src.common.utils.logger import api_logs
from src.edulytica_api.dependencies import get_http_client


events_v1 = APIRouter(prefix="/api/events/v1", tags=["events"])


@api_logs(events_v1.get("", status_code=HTTP_200_OK))
async def list_events(
    auth_data: dict = Depends(access_token_auth),
    session: AsyncSession = Depends(get_session),
):
    """
    Description
        List all events visible to the user, including standard and user-created custom events.

    Args:
        auth_data (dict): Authenticated user data.
        session (AsyncSession): Database session.

    Responses:
        200: {"detail": "Events were found", "events": [{"id": ..., "name": ..., "type": "..."}]}

    Raises:
        HTTPException: On unexpected failures.
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


@api_logs(events_v1.get("/by_name", status_code=HTTP_200_OK))
async def get_event_id(
    auth_data: dict = Depends(access_token_auth),
    event_name: str = Query(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Description
        Return the ID of a standard or user custom event by its name.

    Args:
        auth_data (dict): Authenticated user data.
        event_name (str): Event name to look up.
        session (AsyncSession): Database session.

    Responses:
        200: {"detail": "Event was found", "event_id": "<uuid>"}
        400: {"detail": "Event doesn't exist"}

    Raises:
        HTTPException: On lookup or unexpected failures.
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


@api_logs(events_v1.post("", status_code=HTTP_201_CREATED), exclude_args=['http_client', 'description'])
async def add_custom_event(
    auth_data: dict = Depends(access_token_auth),
    event_name: str = Body(...),
    description: str = Body(...),
    session: AsyncSession = Depends(get_session),
    http_client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Description
        Create a user custom event with the provided name and description.
        Validates the name against the allowed pattern and ensures uniqueness.
        Uploads the description to the RAG service before persisting the event.

    Args:
        auth_data (dict): Authenticated user data.
        event_name (str): New event name.
        description (str): Event description used for RAG indexing.
        session (AsyncSession): Database session.
        http_client (httpx.AsyncClient): HTTP client instance.

    Responses:
        201: {"detail": "Event was created"} (implicit by success)
        400: Invalid/duplicate event name.
        503: RAG service is unavailable.

    Raises:
        HTTPException: For validation and transport errors.
    """
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
                                                  f'/api/rag/v1/upload_text',
                                                  json=rag_payload, timeout=30.0)
            except httpx.RequestError as _re:
                raise HTTPException(
                    status_code=HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"RAG service is unavailable {_re}"
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=HTTP_503_SERVICE_UNAVAILABLE,
                    detail="RAG service failed to process the text upload"
                )

            resp_payload = response.json()
            if resp_payload.get('status') != 'success':
                raise HTTPException(
                    status_code=HTTP_503_SERVICE_UNAVAILABLE,
                    detail="RAG service failed to upload the text"
                )

            await CustomEventCrud.create(
                session=session,
                name=event_name,
                user_id=auth_data['user'].id
            )

            return JSONResponse(
                status_code=HTTP_201_CREATED,
                content={'detail': 'Event was created'}
            )
        else:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Invalid event name specified. Only latin characters, numbers, and ._- are allowed.')
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')
