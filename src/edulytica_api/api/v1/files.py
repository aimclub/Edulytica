"""
Description
    Files API for downloading ticket-related files (original document, summary, result)
    and for extracting parsed text from those files. All endpoints require a valid JWT access token.

Routes:
    GET /{ticket_id}/file         — Download the original uploaded file.
    GET /{ticket_id}/summary      — Download the LLM-generated summary file.
    GET /{ticket_id}/result       — Download the LLM-generated result/report file.
    GET /{ticket_id}/file/text    — Return parsed text from the original file.
    GET /{ticket_id}/result/text  — Return parsed text from the result/report.
"""

from io import BytesIO
from mimetypes import guess_type
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path as FPath
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK

from src.common.auth.auth_bearer import access_token_auth
from src.common.database.crud import TicketCrud, DocumentCrud, DocumentReportCrud, DocumentSummaryCrud
from src.common.database.database import get_session
from src.common.utils.logger import api_logs
from src.edulytica_api.parser.Parser import fast_parse_text


files_v1 = APIRouter(prefix="/api/files/v1", tags=["files"])
ROOT_DIR = Path(__file__).resolve().parents[4]


@api_logs(files_v1.get("/{ticket_id}/file", status_code=HTTP_200_OK))
async def get_ticket_file(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = FPath(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Description
        Download the original file attached to the specified ticket (owned or shared).

    Args:
        auth_data (dict): Authenticated user data.
        ticket_id (UUID): Ticket identifier.
        session (AsyncSession): Database session.

    Responses:
        200: FileResponse with the original file.
        400: Ticket not found / file missing in DB or storage.

    Raises:
        HTTPException: For not found or unexpected errors.
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

        mime, _ = guess_type(str(file_path))

        return FileResponse(
            path=str(file_path),
            media_type=mime or 'application/octet-stream',
            filename=file_path.name)
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')


@api_logs(files_v1.get("/{ticket_id}/summary", status_code=HTTP_200_OK))
async def get_ticket_summary(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = FPath(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Description
        Download the LLM-generated summary file for the specified ticket.

    Args:
        auth_data (dict): Authenticated user data.
        ticket_id (UUID): Ticket identifier.
        session (AsyncSession): Database session.

    Responses:
        200: FileResponse with the summary.
        400: Ticket or summary not found.

    Raises:
        HTTPException: For not found or unexpected errors.
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


@api_logs(files_v1.get("/{ticket_id}/result", status_code=HTTP_200_OK))
async def get_ticket_result(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = FPath(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Description
        Download the LLM-generated result file for the specified ticket.

    Args:
        auth_data (dict): Authenticated user data.
        ticket_id (UUID): Ticket identifier.
        session (AsyncSession): Database session.

    Responses:
        200: FileResponse with the result.
        400: Ticket or result not found.

    Raises:
        HTTPException: For not found or unexpected errors.
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

        mime, _ = guess_type(str(file_path))

        return FileResponse(
            path=str(file_path),
            media_type=mime or 'application/octet-stream',
            filename=file_path.name)
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')


@api_logs(files_v1.get("/{ticket_id}/file/text", status_code=HTTP_200_OK))
async def get_document_text(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = FPath(...),
    session: AsyncSession = Depends(get_session),
):
    """
    Description
        Parse and return text extracted from the original file attached to the ticket.
        Returns an empty string if text cannot be extracted.

    Args:
        auth_data (dict): Authenticated user data.
        ticket_id (UUID): Ticket identifier.
        session (AsyncSession): Database session.

    Responses:
        200: {"detail": "Text extracted", "text": "<string>"}
        400/404: Ticket/document/file not found.

    Raises:
        HTTPException: For not found or unexpected errors.
    """
    try:
        ticket = await TicketCrud.get_ticket_by_id_or_shared(
            session=session, ticket_id=ticket_id, user_id=auth_data["user"].id
        )
        if not ticket:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Ticket not found")

        document = await DocumentCrud.get_by_id(session=session, record_id=ticket.document_id)
        if not document:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Document not found")

        file_path = ROOT_DIR / document.file_path
        if not file_path.exists():
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="File not found")

        try:
            with open(file_path, "rb") as f:
                file_content = f.read()
            file_like = BytesIO(file_content)
            text = fast_parse_text(file_like, filename=file_path.name)
        except Exception:
            text = ""

        return {"detail": "Text extracted", "text": text}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')


@api_logs(files_v1.get("/{ticket_id}/result/text", status_code=HTTP_200_OK))
async def get_result_text(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = FPath(...),
    session: AsyncSession = Depends(get_session),
):
    """
    Description
        Parse and return text extracted from the LLM result/report file of the ticket.
        Returns an empty string if text cannot be extracted.

    Args:
        auth_data (dict): Authenticated user data.
        ticket_id (UUID): Ticket identifier.
        session (AsyncSession): Database session.

    Responses:
        200: {"detail": "Text extracted", "text": "<string>"}
        404: Result or file not found.

    Raises:
        HTTPException: For not found or unexpected errors.
    """
    try:
        ticket = await TicketCrud.get_ticket_by_id_or_shared(
            session=session, ticket_id=ticket_id, user_id=auth_data["user"].id
        )
        if not ticket:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Ticket not found")

        document_report = await DocumentReportCrud.get_by_id(
            session=session, record_id=ticket.document_report_id
        )
        if not document_report:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Result not found")

        file_path = ROOT_DIR / document_report.file_path
        if not file_path.exists():
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="File not found")

        try:
            with open(file_path, "rb") as f:
                file_content = f.read()
            file_like = BytesIO(file_content)
            text = fast_parse_text(file_like, filename=file_path.name) or ""
        except Exception:
            text = ""

        return {"detail": "Text extracted", "text": text}
    except HTTPException as http_exc:  # pragma: no cover
        raise http_exc
    except Exception as _e:  # pragma: no cover
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {_e}')
