import uuid

from pydantic import BaseModel, ConfigDict
import datetime


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    email: str


class UserCreate(UserUpdate):
    username: str
    email: str
    password: str


class UserGet(UserCreate):
    id: uuid.UUID
    username: str
    email: str
    password: str
    disabled: bool


class UserLogin(BaseModel):
    username: str
    password: str


class changepassword(BaseModel):
    username: str
    old_password: str
    new_password: str


class TokenUpdate(BaseModel):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)
    refresh_token: str
    checker: uuid.UUID
    status: bool


class TokenCreate(TokenUpdate):
    user_id: uuid.UUID
    created_date: datetime.datetime


class TokenGet(TokenCreate):
    user_id: uuid.UUID
    refresh_token: str
    checker: uuid.UUID


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
