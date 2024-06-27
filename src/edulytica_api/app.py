import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.edulytica_api.database import SessionLocal, engine
from src.edulytica_api.models import models
from src.edulytica_api.routers.llm_services import *
from src.edulytica_api.routers.auth import *
from src.edulytica_api.routers.norm_services import normocontrol_router

load_dotenv()
# Migration
models.Base.metadata.create_all(bind=engine)
app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)
app.include_router(auth_router)
app.include_router(llm_router)
app.include_router(normocontrol_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
