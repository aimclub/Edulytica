from fastapi import APIRouter
from src.edulytica_api.database import SessionLocal


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

normocontrol_router = APIRouter(prefix="/normocontrol")


@normocontrol_router.post("/auto")
def norm_auto():
    pass


@normocontrol_router.post("/asist")
def norm_asist():
    pass


@normocontrol_router.post("/report")
def norm_report():
    pass
