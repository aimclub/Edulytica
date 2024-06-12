import uuid
from typing import List
from pydantic import BaseModel, ConfigDict
import datetime

class SummarizeData(BaseModel):
    text: List[str]

class PurposeData(BaseModel):
    intro: str
    text: List[List[str]]
