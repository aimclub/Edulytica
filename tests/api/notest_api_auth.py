import json

import pytest

from src.auth.routers.auth import check_code_handler
from src.common.database.database import get_session
from src.common.database.crud.user_crud import UserCrud
from src.common.database.crud.check_code_crud import CheckCodeCrud
from src.common.database.crud.token_crud import TokenCrud


def notest_health_check(client):
    r = client.get("/docs")
    assert r.status_code == 200

    # Valid code successfully activates user and returns access token


def notest_full_auth_flow(client):
    # 1. Registration
    registration_data = {
        "login": "testuser",
        "email": "test@example.com",
        "password1": "securepass",
        "password2": "securepass"
    }
    # Bad also here (background tasks)
    r = client.post("/registration", json=registration_data)
    assert r.status_code == 200
    assert r.json()["detail"] == "Code has been sent"

    # 2. get check code
    import asyncio
    session = asyncio.run(get_session().__anext__())
    user = asyncio.run(
        UserCrud.get_filtered_by_params(
            session,
            email="test@example.com",
            login="testuser"))[0]
    check_code = asyncio.run(CheckCodeCrud.get_filtered_by_params(
        session, user_id=user.id))[-1].code

    # 3. Check code
    r = client.post("/check_code", json={"code": check_code})
    assert r.status_code == 200
    access_token = r.json()["access_token"]
    assert access_token
    refresh_cookie = r.cookies.get("refresh_token")
    assert refresh_cookie and refresh_cookie.startswith("Bearer ")

    # 4. Login
    r = client.post("/login", json={"login": "testuser", "password": "securepass"})
    assert r.status_code == 200
    assert r.json()["detail"] == "Credentials are correct"
    assert "access_token" in r.json()

    # 5. Get Access
    cookies = {"refresh_token": r.cookies.get("refresh_token")}
    r = client.get("/get_access", cookies=cookies)
    assert r.status_code == 200
    assert "access_token" in r.json()

    # 6. Logout
    r = client.get("/logout", cookies=cookies)
    assert r.status_code == 200
    assert r.json()["message"] == "Logout Successful"

    # 7. Token is invalidated
    tokens = asyncio.run(TokenCrud.get_filtered_by_params(session, user_id=user.id))
    assert all(not t.status for t in tokens)
