from fastapi import HTTPException
from starlette import status

from src.edulytica_api.auth.helpers.utils import verify_password


def password_validate(password1, password2):
    if not verify_password(password1, password2):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
