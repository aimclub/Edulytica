from src.edulytica_api.models.files import *

from fastapi import APIRouter, Depends
from src.edulytica_api.database import SessionLocal
from src.edulytica_api.routers.decorators import token_required


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

llm_router = APIRouter(prefix="/llm")
@token_required
@llm_router.post("/purpose")
def get_purpose():
    pass

@token_required
@llm_router.post("/accordance")
def  get_accordance():
    pass

@token_required
@llm_router.post("/summary")
def  get_summary():
    pass
