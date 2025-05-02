import pytest
from datetime import timedelta
from unittest.mock import AsyncMock, patch, ANY
from fastapi import status
from src.auth.app import app
from src.common.auth.helpers.utils import get_hashed_password
from src.common.config import REFRESH_TOKEN_EXPIRE_MINUTES
from src.common.utils.moscow_datetime import datetime_now_moscow


@pytest.mark.asyncio
@patch("src.auth.routers.auth.UserCrud.get_filtered_by_params")
@patch("src.auth.routers.auth.UserRoleCrud.get_filtered_by_params")
@patch("src.auth.routers.auth.UserCrud.create")
@patch("src.auth.routers.auth.CheckCodeCrud.create")
@patch("src.auth.routers.auth.send_email")
async def test_registration_success(
        mock_send_email,
        mock_check_code_create,
        mock_user_create,
        mock_role_get,
        mock_user_get,
        client,
):
    mock_user_get.return_value = []
    mock_role_get.return_value = [AsyncMock(id=1)]
    mock_user_create.return_value = AsyncMock(id=123)

    payload = {
        "login": "newuser",
        "email": "new@example.com",
        "password1": "securepass",
        "password2": "securepass"
    }

    response = client(app).post("/registration", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "Code has been sent"}
    mock_send_email.assert_called_once()


@pytest.mark.asyncio
@patch("src.auth.routers.auth.UserCrud.get_filtered_by_params")
async def test_registration_existing_email(mock_user_get, client):
    mock_user_get.side_effect = [[AsyncMock()], []]

    response = client(app).post("/registration", json={
        "login": "newuser",
        "email": "existing@example.com",
        "password1": "securepass",
        "password2": "securepass"
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "User with such email already exists"


@pytest.mark.asyncio
@patch("src.auth.routers.auth.UserCrud.get_filtered_by_params")
async def test_registration_existing_login(mock_user_get, client):
    mock_user_get.side_effect = [[], [AsyncMock()]]

    response = client(app).post("/registration", json={
        "login": "existinguser",
        "email": "new@example.com",
        "password1": "securepass",
        "password2": "securepass"
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "User with such login already exists"


@pytest.mark.asyncio
@patch("src.auth.routers.auth.UserCrud.get_filtered_by_params")
async def test_registration_password_mismatch(mock_user_get, client):
    mock_user_get.side_effect = [[], []]

    response = client(app).post("/registration", json={
        "login": "user1",
        "email": "user1@example.com",
        "password1": "pass1",
        "password2": "pass2"
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Passwords are not equal"


@pytest.mark.asyncio
@patch("src.auth.routers.auth.CheckCodeCrud.get_recent_code")
@patch("src.auth.routers.auth.UserCrud.get_by_id")
@patch("src.auth.routers.auth.UserCrud.get_active_user_by_email_or_login")
@patch("src.auth.routers.auth.UserCrud.update")
@patch("src.auth.routers.auth.TokenCrud.create")
def test_check_code_success(
    mock_token_create,
    mock_user_update,
    mock_get_active_user,
    mock_get_by_id,
    mock_get_recent_code,
    client
):
    mock_get_recent_code.return_value = AsyncMock(user_id=1)
    mock_get_by_id.return_value = AsyncMock(
        id=1, login="user1", email="user1@example.com"
    )
    mock_get_active_user.return_value = None

    response = client(app).post("/check_code", json={"code": "123456"})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["detail"] == "Code is correct"
    cookies = response.cookies
    assert "refresh_token" in cookies
    cookie_value = cookies.get("refresh_token").strip('"')
    assert cookie_value.startswith("Bearer ")


@pytest.mark.asyncio
@patch("src.auth.routers.auth.CheckCodeCrud.get_recent_code")
def test_check_code_invalid_code(mock_get_recent_code, client):
    mock_get_recent_code.return_value = None

    response = client(app).post("/check_code", json={"code": "wrong"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Wrong code"


@pytest.mark.asyncio
@patch("src.auth.routers.auth.CheckCodeCrud.get_recent_code")
@patch("src.auth.routers.auth.UserCrud.get_by_id")
@patch("src.auth.routers.auth.UserCrud.get_active_user_by_email_or_login")
def test_check_code_user_exists(
        mock_get_active_user,
        mock_get_by_id,
        mock_get_recent_code,
        client
):
    mock_get_recent_code.return_value = AsyncMock(user_id=1)
    mock_get_by_id.return_value = AsyncMock(
        id=1, login="user1", email="user1@example.com"
    )
    mock_get_active_user.return_value = AsyncMock(
        id=1, login="user1", email="user1@example.com", is_active=True
    )

    response = client(app).post("/check_code", json={"code": "123456"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "User with such email or login already is active"


@pytest.mark.asyncio
@patch("src.auth.routers.auth.UserCrud.get_filtered_by_params")
@patch("src.auth.routers.auth.TokenCrud.create")
def test_login_success(
    mock_token_create,
    mock_user_get,
    client
):
    mock_user_get.return_value = [
        AsyncMock(id=1, login="user1", email="user@example.com",
                  password_hash=get_hashed_password('testpassword'))
    ]

    response = client(app).post("/login", json={
        "login": "user1",
        "password": "testpassword"
    })

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["detail"] == "Credentials are correct"
    assert "access_token" in data

    cookie_value = response.cookies.get("refresh_token").strip('"')
    assert cookie_value.startswith("Bearer ")


@pytest.mark.asyncio
@patch("src.auth.routers.auth.UserCrud.get_filtered_by_params")
def test_login_user_not_found(mock_user_get, client):
    mock_user_get.return_value = []

    response = client(app).post("/login", json={
        "login": "unknown",
        "password": "any"
    })

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Credentials are incorrect"


@pytest.mark.asyncio
@patch("src.auth.routers.auth.UserCrud.get_filtered_by_params")
@patch("src.auth.routers.auth.verify_password")
def test_login_wrong_password(mock_verify_password, mock_user_get, client):
    mock_user_get.return_value = [
        AsyncMock(id=1, login="user1", email="user@example.com",
                  password_hash=get_hashed_password('testpassword'))
    ]
    mock_verify_password.return_value = False

    response = client(app).post("/login", json={
        "login": "user1",
        "password": "wrong-password"
    })

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Credentials are incorrect"


@pytest.mark.asyncio
@patch("src.auth.routers.auth.TokenCrud.get_filtered_by_params")
@patch("src.auth.routers.auth.TokenCrud.create")
def test_get_access_success(mock_token_create, mock_token_get, client):
    mock_token_get.return_value = [
        AsyncMock(
            created_at=datetime_now_moscow() - timedelta(minutes=5)
        )
    ]

    response = client(app).get("/get_access")

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    cookie_value = response.cookies.get("refresh_token").strip('"')
    assert cookie_value.startswith("Bearer ")


@pytest.mark.asyncio
@patch("src.auth.routers.auth.TokenCrud.get_filtered_by_params")
def test_get_access_token_not_found(mock_token_get, client):
    mock_token_get.return_value = []

    response = client(app).get("/get_access")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Token is incorrect"
    assert response.cookies.get("refresh_token") is None


@pytest.mark.asyncio
@patch("src.auth.routers.auth.TokenCrud.get_filtered_by_params")
@patch("src.auth.routers.auth.datetime_now_moscow")
def test_get_access_expired_token(mock_datetime, mock_token_get, client):
    mock_datetime.return_value = datetime_now_moscow()

    expired_time = datetime_now_moscow() - timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES + 5)
    mock_token_get.return_value = [
        AsyncMock(created_at=expired_time)
    ]

    response = client(app).get("/get_access")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Token is incorrect"
    assert response.cookies.get("refresh_token") is None


@pytest.mark.asyncio
@patch("src.auth.routers.auth.TokenCrud.get_filtered_by_params")
@patch("src.auth.routers.auth.TokenCrud.delete")
def test_logout_success(mock_token_delete, mock_token_get, client):
    mock_token_get.return_value = [AsyncMock(id=42)]

    response = client(app).get("/logout")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Logout Successful"
    assert response.cookies.get("refresh_token") is None
    mock_token_delete.assert_called_once_with(session=ANY, record_id=42)


@pytest.mark.asyncio
@patch("src.auth.routers.auth.TokenCrud.get_filtered_by_params")
def test_logout_token_not_found(mock_token_get, client):
    mock_token_get.return_value = []

    response = client(app).get("/logout")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Exception in token validation"
