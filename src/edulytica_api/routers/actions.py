import os
import uuid
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, Body, UploadFile, Depends, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST
from src.common.auth.auth_bearer import access_token_auth
from src.common.database.crud.document_report_crud import DocumentReportCrud
from src.common.database.crud.document_summary_crud import DocumentSummaryCrud
from src.common.database.crud.event_crud import EventCrud
from src.common.database.crud.custom_event_crud import CustomEventCrud
from src.common.database.crud.document_crud import DocumentCrud
from src.common.database.crud.ticket_status_crud import TicketStatusCrud
from src.common.database.crud.ticket_type_crud import TicketTypeCrud
from src.common.database.crud.tickets_crud import TicketCrud
from src.common.database.database import get_session
from src.common.database.models import DocumentSummary
from src.common.utils.default_enums import TicketStatusDefault, TicketTypeDefault
from src.common.utils.logger import api_logs
from src.edulytica_api.parser.Parser import get_structural_paragraphs
from src.edulytica_api.celery.tasks import get_llm_purpose_result

actions_router = APIRouter(prefix="/actions")
ROOT_DIR = Path(__file__).resolve().parents[2]


@api_logs(actions_router.post("/new_ticket"))
async def new_ticket(
    auth_data: dict = Depends(access_token_auth),
    file: UploadFile = File(...),
    event_id: UUID = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    try:
        custom_event = None
        event = await EventCrud.get_by_id(
            session=session,
            record_id=event_id
        )
        if not event:
            custom_event = await CustomEventCrud.get_by_id(
                session=session,
                record_id=event_id
            )

        if not (event or custom_event):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Incorrect event id'
            )

        if file.content_type not in [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]:
            raise HTTPException(
                status_code=400,
                detail='Invalid file type, only PDF or DOCX'
            )

        file_extension = (file.filename or '').rsplit('.', 1)[-1].lower()
        while True:
            file_id = uuid.uuid4()

            if not await DocumentCrud.get_by_id(
                    session=session, id=file_id
            ):
                break

        file_path = os.path.join(
            'app_files',
            'document',
            f'{auth_data["user"].id}',
            f'{file_id}.{file_extension}')

        with open(os.path.join(ROOT_DIR, file_path), 'wb') as f:
            f.write(await file.read())

        await DocumentCrud.create(
            session=session, user_id=auth_data['user'].id, file_path=file_path, id=file_id
        )

        ticket_status = await TicketStatusCrud.get_filtered_by_params(
            session=session, name=TicketStatusDefault.IN_PROGRESS.value
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
        ticket = await TicketCrud.create(
            **ticket_data
        )

        # Добавляем в очередь обработку документа
        data = get_structural_paragraphs(file.file)
        intro = " ".join(data['table_of_content'][0]['text'])
        main_text = " ".join(data['other_text'])
        task = get_llm_purpose_result.delay(
            intro=intro,
            main_text=main_text,
            user_id=auth_data['user'].id,
            ticket_id=ticket.id)

        return {'detail': 'Ticket has been created', 'ticket_id': ticket.id}
    except Exception as _e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(actions_router.get("/get_event_id"))
async def get_event_id(
    auth_data: dict = Depends(access_token_auth),
    event_name: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    try:
        event = await EventCrud.get_filtered_by_params(
            session=session,
            name=event_name
        )
        if not event:
            event = await CustomEventCrud.get_filtered_by_params(
                session=session,
                name=event_name,
                user_id=auth_data['user'].id
            )

        if not event:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Event doesn\'t exist'
            )

        return {'detail': 'Event was found', 'event_id': event.id}

    except Exception as _e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(actions_router.get("/get_ticket"))
async def get_ticket(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    try:
        ticket = await TicketCrud.get_ticket_by_id_or_shared(
            session=session,
            ticket_id=ticket_id,
            user_id=auth_data['user'].id
        )

        if not ticket:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Ticket doesn\'t exist or you\'re not ticket creator'
            )

        return {'detail': 'Ticket was found', 'ticket': ticket[0]}
    except Exception as _e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(actions_router.get("/get_ticket_file"))
async def get_ticket_file(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    try:
        ticket = await TicketCrud.get_ticket_by_id_or_shared(
            session=session,
            ticket_id=ticket_id,
            user_id=auth_data['user'].id
        )
        if not ticket:
            raise HTTPException(
                status_code=400,
                detail='Ticket doesn\'t exist')

        document = await DocumentCrud.get_by_id(
            session=session,
            record_id=ticket.document_id
        )
        if not document:
            raise HTTPException(
                status_code=400,
                detail='File not found'
            )

        file_path = ROOT_DIR / document.file_path
        if not file_path.exists():
            raise HTTPException(
                status_code=400,
                detail='File not found'
            )

        return FileResponse(
            path=str(file_path),
            media_type='application/octet-stream',
            filename=file_path.name
        )
    except Exception as _e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(actions_router.get("/get_ticket_summary"))
async def get_ticket_summary(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    try:
        ticket = await TicketCrud.get_ticket_by_id_or_shared(
            session=session,
            ticket_id=ticket_id,
            user_id=auth_data['user'].id
        )
        if not ticket:
            raise HTTPException(
                status_code=400,
                detail='Ticket doesn\'t exist')

        document_summary = await DocumentSummaryCrud.get_by_id(
            session=session,
            record_id=ticket.document_summary_id
        )
        if not document_summary:
            raise HTTPException(
                status_code=400,
                detail='Ticket summary not found'
            )

        file_path = ROOT_DIR / document_summary.file_path
        if not file_path.exists():
            raise HTTPException(
                status_code=400,
                detail='Ticket summary not found'
            )

        return FileResponse(
            path=str(file_path),
            media_type='application/octet-stream',
            filename=file_path.name
        )
    except Exception as _e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(actions_router.get("/get_ticket_result"))
async def get_ticket_result(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    try:
        ticket = await TicketCrud.get_ticket_by_id_or_shared(
            session=session,
            ticket_id=ticket_id,
            user_id=auth_data['user'].id
        )
        if not ticket:
            raise HTTPException(
                status_code=400,
                detail='Ticket doesn\'t exist')

        document_report = await DocumentReportCrud.get_by_id(
            session=session,
            record_id=ticket.document_id
        )
        if not document_report:
            raise HTTPException(
                status_code=400,
                detail='Ticket result not found'
            )

        file_path = ROOT_DIR / document_report.file_path
        if not file_path.exists():
            raise HTTPException(
                status_code=400,
                detail='Ticket result not found'
            )

        return FileResponse(
            path=str(file_path),
            media_type='application/octet-stream',
            filename=file_path.name
        )
    except Exception as _e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )


@api_logs(actions_router.post("/ticket_share"))
async def ticket_share(
    auth_data: dict = Depends(access_token_auth),
    ticket_id: UUID = Body(..., embed=True),
    session: AsyncSession = Depends(get_session)
):
    try:
        ticket = await TicketCrud.get_filtered_by_params(
            session=session,
            user_id=auth_data['user'].id,
            id=ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='You aren\'t ticket owner or ticket doesn\'t exist'
            )

        await TicketCrud.update(
            session=session,
            record_id=ticket_id,
            shared=(not ticket.shared)
        )

        return {
            'detail': 'Status has been changed'
        }
    except Exception as _e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'500 ERR: {_e}'
        )
