import os
from typing import List
from dotenv import load_dotenv
from src.common.utils.split_csv import split_csv


load_dotenv()


POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_IP = os.environ.get("POSTGRES_IP")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES"))
ALGORITHM = os.environ.get("ALGORITHM")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.environ.get("JWT_REFRESH_SECRET_KEY")
ALLOWED_ORIGINS: List[str] = split_csv(os.environ.get("ALLOWED_ORIGINS", ""))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = int(os.environ.get("SMTP_PORT"))
EMAIL_CODE_EXPIRE_SECONDS = int(os.environ.get("EMAIL_CODE_EXPIRE_SECONDS"))
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
LLM_KAFKA_BOOTSTRAP_SERVERS = os.environ.get("LLM_KAFKA_BOOTSTRAP_SERVERS")
KAFKA_GROUP_ID = os.environ.get("KAFKA_GROUP_ID")
INTERNAL_API_SECRET = os.environ.get("INTERNAL_API_SECRET")
REDIS_PORT = int(os.environ.get("REDIS_PORT"))
API_PORT = int(os.environ.get("API_PORT"))
AUTH_PORT = int(os.environ.get("AUTH_PORT"))
ORCHESTRATOR_PORT = int(os.environ.get("ORCHESTRATOR_PORT"))
RAG_PORT = int(os.environ.get("RAG_PORT"))
FRONTEND_PORT = int(os.environ.get("FRONTEND_PORT"))
CHROMA_PORT = int(os.environ.get("CHROMA_PORT"))
CHAT_THREAD_ID = int(os.environ.get("CHAT_THREAD_ID", 0))
CHAT_ID = int(os.environ.get("CHAT_ID"))
BOT_TOKEN = os.environ.get("BOT_TOKEN")
