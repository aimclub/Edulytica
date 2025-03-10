import uuid
from typing import List

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict
import datetime

from src.edulytica_api.models.models import ResultFiles


class UploadFileData(BaseModel):
    file: UploadFile


class ResultFilesUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    file: str


class ResultFilesCreate(ResultFilesUpdate):
    user_id: uuid.UUID
    ticket_id: uuid.UUID


class ResultFilesGet(ResultFilesCreate):
    id: uuid.UUID


class TicketStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str


class TicketsUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    ticket_type: str
    user_id: uuid.UUID
    status_id: int


class TicketsCreate(TicketsUpdate):
    pass


class TicketsGet(TicketsCreate):
    result_files: List[ResultFilesGet]
    status: TicketStatus


class TicketGetResponse(BaseModel):
    id: uuid.UUID
