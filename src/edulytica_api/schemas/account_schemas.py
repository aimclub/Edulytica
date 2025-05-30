from pydantic import BaseModel, Field
from typing import Optional


class EditProfileRequest(BaseModel):
    name: Optional[str] = Field(None)
    surname: Optional[str] = Field(None)
    organization: Optional[str] = Field(None)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(...)
    new_password1: str = Field(...)
    new_password2: str = Field(...)
