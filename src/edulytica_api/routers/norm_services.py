from src.edulytica_api.models.files import *

from fastapi import APIRouter, Depends
from src.edulytica_api.database import SessionLocal
from src.edulytica_api.routers.auth_bearer import JWTBearer
from src.edulytica_api.routers.decorators import token_required


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

normocontrol_router = APIRouter(prefix="/normocontrol")

@token_required
@normocontrol_router.post("/auto")
def norm_auto():
    pass

@token_required
@normocontrol_router.post("/asist")
def norm_asist():
    pass

@token_required
@normocontrol_router.post("/report")
def norm_report():
    pass
