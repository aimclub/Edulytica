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
    id: int
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class changepassword(BaseModel):
    username: str
    old_password: str
    new_password: str


class TokenCreate(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str
    status: bool
    created_date: datetime.datetime