import uuid
import pytest
from jose import jwt
from fastapi import Request, HTTPException, FastAPI, Depends
from fastapi.testclient import TestClient
from starlette.datastructures import Headers
from src.common.auth.helpers.utils import (
    get_hashed_password, verify_password,
    create_access_token, create_refresh_token,
    get_expiry, OAuth2PasswordBearerWithCookie,
    ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
)
from src.common.auth.helpers.validators import password_validate
from src.common.config import JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY, ALGORITHM


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")


@app.get("/refresh")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    return {"token": token}


def test_get_hashed_and_verify_password():
    password = "supersecret"
    hashed = get_hashed_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_password_validate_success():
    plain_password = "superpassword"
    hashed_password = get_hashed_password(plain_password)
    try:
        password_validate(plain_password, hashed_password)
    except HTTPException:
        pytest.fail("password_validate raised HTTPException unexpectedly!")


def test_password_validate_failure():
    plain_password = "correctpassword"
    wrong_password = "wrongpassword"
    hashed_password = get_hashed_password(plain_password)

    with pytest.raises(HTTPException) as exc_info:
        password_validate(wrong_password, hashed_password)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Incorrect email or password"



def test_create_access_token():
    subject = "example_user"
    token = create_access_token(subject)
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    assert payload['sub'] == subject
    assert payload['token_type'] == ACCESS_TOKEN_TYPE


def test_create_refresh_token():
    subject = "example_user"
    checker = uuid.uuid4()
    token = create_refresh_token(subject, checker)
    payload = jwt.decode(token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    assert payload['sub'] == subject
    assert payload['checker'] == str(checker)
    assert payload['token_type'] == REFRESH_TOKEN_TYPE


def test_get_expiry():
    expiry_str = get_expiry(10)
    assert isinstance(expiry_str, str)
    assert expiry_str.endswith('GMT')


@pytest.mark.asyncio
async def test_oauth2_bearer_token():
    oauth = OAuth2PasswordBearerWithCookie(tokenUrl="token")

    request = Request({
        "type": "http",
        "headers": Headers({"authorization": "Bearer testtoken"}).raw,
        "method": "GET",
        "path": "/protected",
        "query_string": b"",
        "server": ("testserver", 80),
    })

    token = await oauth(request)
    assert token == "testtoken"


@pytest.mark.asyncio
async def test_oauth2_cookie_token():
    client = TestClient(app)
    response = client.get("/refresh", cookies={"refresh_token": "Bearer cookie_token"})

    assert response.status_code == 200
    assert response.json() == {"token": "cookie_token"}

@pytest.mark.asyncio
async def test_oauth2_missing_token():
    oauth = OAuth2PasswordBearerWithCookie(tokenUrl="token")

    request = Request({
        "type": "http",
        "headers": Headers({}).raw,
        "method": "GET",
        "path": "/protected",
        "query_string": b"",
        "server": ("testserver", 80),
    })

    with pytest.raises(HTTPException) as exc_info:
        await oauth(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"
