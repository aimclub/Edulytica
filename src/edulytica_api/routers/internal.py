import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException, Depends, UploadFile, File, Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR

from src.common.config import INTERNAL_API_SECRET
from src.common.database.crud.document_report_crud import DocumentReportCrud
from src.common.database.crud.ticket_status_crud import TicketStatusCrud
from src.common.database.crud.tickets_crud import TicketCrud
from src.common.database.database import get_session
from src.common.utils.default_enums import TicketStatusDefault
from src.common.utils.logger import api_logs


ROOT_DIR = Path(__file__).resolve().parents[2]
internal_router = APIRouter(prefix="/internal")


async def verify_internal_secret(x_internal_secret: str = Header(...)):
    if not INTERNAL_API_SECRET or x_internal_secret != INTERNAL_API_SECRET:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid internal secret key"
        )


@api_logs(internal_router.post("/upload_report", dependencies=[Depends(verify_internal_secret)]))
async def upload_report(
        ticket_id: uuid.UUID = Body(...),
        report_text: str = Body(...),
        session: AsyncSession = Depends(get_session)
):
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
