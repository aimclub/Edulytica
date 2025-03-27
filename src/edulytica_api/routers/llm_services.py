import os
import uuid
from pathlib import Path
from starlette import status
from starlette.responses import FileResponse
from src.edulytica_api.parser.Parser import get_structural_paragraphs
from src.edulytica_api.celery.tasks import get_llm_purpose_result, get_llm_summary_result
from src.edulytica_api.crud.result_files_crud import ResultFilesCrud
from src.edulytica_api.crud.tickets_crud import TicketsCrud
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from src.edulytica_api.database import get_session
from src.edulytica_api.auth.auth_bearer import access_token_auth
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
import json
from src.edulytica_api.schemas.llm_schema import TicketGetResponse
from src.edulytica_api.utils.logger import api_logs

llm_router = APIRouter(prefix="/llm")
ROOT_DIR = Path(__file__).resolve().parents[1]


@api_logs(llm_router.post("/purpose"))
async def get_purpose(
    file: UploadFile,
    auth_data: Annotated[dict, Depends(access_token_auth)],
    session: AsyncSession = Depends(get_session)
):
    user = auth_data['user']
    data = get_structural_paragraphs(file.file)
    intro = " ".join(data['table_of_content'][0]['text'])
    main_text = " ".join(data['other_text'])

    ticket = await TicketsCrud.create(
        session=session, ticket_type='Достижимость', user_id=user.id, status_id=0
    )
    task = get_llm_purpose_result.delay(
        intro=intro,
        main_text=main_text,
        user_id=user.id,
        ticket_id=ticket.id)
    return json.dumps(task.id)


@api_logs(llm_router.post("/summary"))
async def get_summary(
    file: UploadFile,
    auth_data: Annotated[dict, Depends(access_token_auth)],
    session: AsyncSession = Depends(get_session)
):
    def split_on_para(text_list, content):
        if content['text'] is not None:
            if len(content['text']) > 1:
                text_list.append(" ".join(content['text']))
        if 'sub_elements' in content.keys():
            for sub in content['sub_elements']:
                split_on_para(text_list, sub)
        else:
            return text_list

    user = auth_data['user']
    data = get_structural_paragraphs(file.file)
    text_list = []

    for content in data['table_of_content']:
        split_on_para(text_list, content)

    ticket = await TicketsCrud.create(
        session=session, ticket_type='Суммаризация', user_id=user.id, status_id=0
    )
    task = get_llm_summary_result.delay(main_text=text_list, user_id=user.id, ticket_id=ticket.id)
    return json.dumps(task.id)


@api_logs(llm_router.get("/results"))
async def get_results(
    auth_data: Annotated[dict, Depends(access_token_auth)],
    session: AsyncSession = Depends(get_session)
):
    user = auth_data['user']
    tickets = await TicketsCrud.get_filtered_by_params(session=session, user_id=user.id)
    return tickets


@api_logs(llm_router.post("/result"))
async def get_result(
    ticket_resp: TicketGetResponse,
    auth_data: Annotated[dict, Depends(access_token_auth)],
    session: AsyncSession = Depends(get_session)
):
    user = auth_data['user']
    try:
        ticket = await TicketsCrud.get_by_id(session=session, record_id=ticket_resp.id)
        if ticket is not None:
            data = {'status': 'In progress'}
            if len(ticket.result_files) > 0:
                result_file = ticket.result_files[0]
                file_path = os.path.join(ROOT_DIR, result_file.file)
                with open(file_path, mode='r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['status'] = 'Ready'
            if ticket.user_id == user.id:
                return {'ticket': ticket, 'result_data': data}
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not Permission"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='BAD_REQUEST'
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='BAD_REQUEST'
        )


@api_logs(llm_router.get("/file/{file_id}", response_class=FileResponse))
async def get_file(
    file_id: uuid.UUID,
    auth_data: Annotated[dict, Depends(access_token_auth)],
    session: AsyncSession = Depends(get_session)
):
    try:
        file = await ResultFilesCrud.get_by_id(session=session, record_id=file_id)
        if file.user_id == auth_data['user'].id:
            return os.path.join(ROOT_DIR, file.file)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='BAD_REQUEST'
            )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='BAD_REQUEST'
        )
