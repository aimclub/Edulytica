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
    DELETE /actions/delete_ticket: Deletes a ticket owned by the user.
    POST /actions/ticket_share: Toggles the shared status of a ticket.
"""

import httpx

from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST, HTTP_503_SERVICE_UNAVAILABLE

from src.common.auth.auth_bearer import access_token_auth
from src.common.config import BOT_TOKEN, CHAT_ID, CHAT_THREAD_ID
from src.common.database.schemas.feedback_schema import FeedbackIn
from src.common.utils.emv2 import emv2
from src.common.utils.logger import api_logs
from src.edulytica_api.dependencies import get_http_client


feedback_v1 = APIRouter(prefix="/api/feedback/v1", tags=["actions"])


@api_logs(feedback_v1.post(''), exclude_args=['http_client', 'payload'])
async def send_feedback_to_telegram(
    auth_data: dict = Depends(access_token_auth),
    payload: FeedbackIn = Body(...),
    http_client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Sends feedback to a Telegram **topic** (forum thread) using MarkdownV2 formatting.

    Args:
        auth_data (dict): Authenticated user data.
        payload (FeedbackIn): Validated feedback payload (EmailStr ensures proper email).
        http_client (AsyncClient): Async HTTP Client.

    Returns:
        dict: Message confirming delivery with Telegram message id.

    Raises:
        HTTPException:
            400: Empty name/text.
            503: Telegram API is unreachable.
            500: Misconfiguration or Telegram API error.
    """
    try:
        if len(payload.name) > 100:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='The name is too long, maximum 100 characters'
            )

        if len(str(payload.email)) > 100:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='The email is too long, maximum 100 characters'
            )

        if len(payload.text) > 3000:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='The text is too long, maximum 3000 characters'
            )

        msg = (
            f"ФИО: {emv2(payload.name.strip())}\n"
            f"email: `{payload.email}`\n\n"
            f"{emv2(payload.text.strip())}"
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        body = {
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "MarkdownV2",
        }

        if CHAT_THREAD_ID > 0:
            body["message_thread_id"] = CHAT_THREAD_ID

        try:
            resp = await http_client.post(url, json=body, timeout=30.0)
            resp.raise_for_status()
        except httpx.RequestError as _re:
            raise HTTPException(
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Telegram API is unavailable: {_re}"
            )
        except httpx.HTTPStatusError as _hse:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Telegram API error: {_hse.response.text}"
            )

        data = resp.json()
        if not data.get("ok"):
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Telegram returned an error: {data.get('description')}"
            )

        return {"detail": "Feedback sent"}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"500 ERR: {_e}"
        )
