import uuid
from typing import List

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict
import datetime

class SummarizeData(BaseModel):
    text: List[str]

class PurposeData(BaseModel):
    file: UploadFile

