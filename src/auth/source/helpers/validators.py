"""
This module provides a utility function for password validation in authentication workflows.
"""

from fastapi import HTTPException
from starlette import status
from src.auth.source.helpers.utils import verify_password


def password_validate(password1: str, password2: str):
    """
    Validates a password by comparing it with a hashed password.

    Args:
        password1 (str): The plain-text password entered by the user.
        password2 (str): The hashed password stored in the database.

    Raises:
        HTTPException: If the passwords do not match, an error is raised with status code 400.
    """
    if not verify_password(password1, password2):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
