from fastapi import APIRouter

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
