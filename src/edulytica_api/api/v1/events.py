import httpx

from fastapi import APIRouter, Depends, Body, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_503_SERVICE_UNAVAILABLE, HTTP_500_INTERNAL_SERVER_ERROR

from src.common.auth.auth_bearer import access_token_auth
from src.common.config import RAG_PORT
from src.common.database.crud import EventCrud, CustomEventCrud
from src.common.database.database import get_session
from src.common.utils.chroma_utils import is_valid_chroma_collection_name
from src.common.utils.logger import api_logs
from src.edulytica_api.dependencies import get_http_client


events_v1 = APIRouter(prefix="/api/events/v1", tags=["events"])


@api_logs(events_v1.get(""))
async def list_events(
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


@api_logs(events_v1.get("/by_name"))
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


@api_logs(events_v1.post(""), exclude_args=['http_client', 'description'])
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
                                                  f'/api/rag/v1/upload_text',
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
