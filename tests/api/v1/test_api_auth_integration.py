import uuid
import pytest
from unittest.mock import patch
from src.common.utils.check_code_utils import generate_code

test_user_data = {
    "login": f"testuser_{uuid.uuid4().hex[:8]}",
    "email": f"{uuid.uuid4().hex[:8]}@example.com",
    "password1": "securepass",
    "password2": "securepass"
}
static_code = generate_code()


@pytest.mark.order(1)
@patch("src.auth.api.v1.auth.send_email")
@patch("src.auth.api.v1.auth.generate_code")
def test_registration_success(mock_generate_code, mock_send_email, integration_client):
    mock_generate_code.return_value = static_code

    response = integration_client.post("/api/auth/v1/registration", json=test_user_data)
    assert response.status_code == 200
    assert response.json()["detail"] == "Code has been sent"
    mock_send_email.assert_called_once()


@pytest.mark.order(2)
def test_check_code_success(integration_client):
    response = integration_client.post("/api/auth/v1check_code", json={"code": static_code})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert integration_client.cookies.get("refresh_token", "").strip('"').startswith("Bearer")


@pytest.mark.order(3)
def test_login_success(integration_client):
    response = integration_client.post("/api/auth/v1/login", json={
        "login": test_user_data["login"],
        "password": test_user_data["password1"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.order(4)
def test_get_access_success(integration_client):
    login_resp = integration_client.post("/api/auth/v1/login", json={
        "login": test_user_data["login"],
        "password": test_user_data["password1"]
    })

    assert login_resp.status_code == 200

    refresh_token = login_resp.cookies.get("refresh_token")
    assert refresh_token

    response = integration_client.get("/api/auth/v1/get_access", cookies={
        "refresh_token": refresh_token
    })

    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.order(5)
def test_logout_success(integration_client):
    login_resp = integration_client.post("/api/auth/v1/login", json={
        "login": test_user_data["login"],
        "password": test_user_data["password1"]
    })
    assert login_resp.status_code == 200

    refresh_token = login_resp.cookies.get("refresh_token")
    assert refresh_token

    response = integration_client.get("/api/auth/v1/logout", cookies={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert response.json()["message"] == "Logout Successful"
