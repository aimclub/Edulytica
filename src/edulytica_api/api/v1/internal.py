"""
Description
    Internal API used by backend services to upload generated reports and mutate ticket metadata.
    Access is restricted via the `X-Internal-Secret` header.

Routes:
    POST /upload_report     — Save a plain-text report file and mark the ticket completed.
    POST /edit_ticket_name  — Update the ticket name.
Security:
    Header: X-Internal-Secret (must match server-side secret).
"""

import os
import uuid

from pathlib import Path
from fastapi import APIRouter, Header, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK

from src.common.config import INTERNAL_API_SECRET
from src.common.database.crud.document_report_crud import DocumentReportCrud
from src.common.database.crud.ticket_status_crud import TicketStatusCrud
from src.common.database.crud.ticket_crud import TicketCrud
from src.common.database.database import get_session
from src.common.utils.default_enums import TicketStatusDefault
from src.common.utils.logger import api_logs


ROOT_DIR = Path(__file__).resolve().parents[4]
internal_v1 = APIRouter(prefix="/api/internal/v1", tags=['internal'])


async def verify_internal_secret(x_internal_secret: str = Header(...)):
    if not INTERNAL_API_SECRET or x_internal_secret != INTERNAL_API_SECRET:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid internal secret key"
        )


@api_logs(
    internal_v1.post("/upload_report", dependencies=[Depends(verify_internal_secret)], status_code=HTTP_200_OK),
    exclude_args=['report_text']
)
async def upload_report(
        ticket_id: uuid.UUID = Body(...),
        report_text: str = Body(...),
        session: AsyncSession = Depends(get_session)
):
    """
    Description
        Persist the provided report text as a file, create a report record, and mark the ticket as completed.

    Args:
        ticket_id (UUID): Ticket to attach the report to.
        report_text (str): Plain-text report contents.
        session (AsyncSession): Database session.

    Responses:
        200: {"detail": "Report has been uploaded and ticket is marked as completed", "report_id": "<uuid>"}
        403: Invalid internal secret key.

    Raises:
        HTTPException: For authorization failures or unexpected errors.
    """

    try:
        ticket = await TicketCrud.get_by_id(session=session, record_id=ticket_id)

        report_id = uuid.uuid4()

        file_dir = os.path.join(ROOT_DIR, 'app_files', 'report', str(ticket.user_id))
        os.makedirs(file_dir, exist_ok=True)
        saved_file_path = os.path.join(file_dir, f'{report_id}.txt')

        with open(saved_file_path, 'w', encoding='utf-8') as f:
            f.write(report_text)

        db_report_path = os.path.join(
            'app_files', 'report', str(ticket.user_id), f'{report_id}.txt'
        )
        await DocumentReportCrud.create(
            session=session, id=report_id, file_path=db_report_path
        )

        completed_status = (await TicketStatusCrud.get_filtered_by_params(
            session=session, name=TicketStatusDefault.COMPLETED.value
        ))[0]

        await TicketCrud.update(
            session=session,
            record_id=ticket_id,
            document_report_id=report_id,
            ticket_status_id=completed_status.id
        )

        return {
            "detail": "Report has been uploaded and ticket is marked as completed",
            "report_id": report_id}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {e}')


@api_logs(internal_v1.post("/edit_ticket_name", dependencies=[Depends(verify_internal_secret)], status_code=HTTP_200_OK))
async def edit_ticket_name(
        ticket_id: uuid.UUID = Body(...),
        name: str = Body(...),
        session: AsyncSession = Depends(get_session)
):
    """
    Description
        Update the ticket name by ID.

    Args:
        ticket_id (UUID): Ticket identifier.
        name (str): New ticket name.
        session (AsyncSession): Database session.

    Responses:
        200: {"detail": "Ticket name has been edited"}
        403: Invalid internal secret key.

    Raises:
        HTTPException: For authorization failures or unexpected errors.
    """
    try:
        await TicketCrud.update(session, record_id=ticket_id, name=name)
        return {
            "detail": "Ticket name has been edited",
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f'500 ERR: {e}')
