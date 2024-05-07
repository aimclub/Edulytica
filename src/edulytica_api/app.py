import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from src.edulytica_api.database import SessionLocal, engine
from src.edulytica_api.models import auth
from src.edulytica_api.routers.llm_services import *
from src.edulytica_api.routers.auth import *
from src.edulytica_api.routers.norm_services import normocontrol_router

load_dotenv()
auth.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(auth_router)
app.include_router(llm_router)
app.include_router(normocontrol_router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)