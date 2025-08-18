import pytest
from unittest.mock import patch
from fastapi import status
from edulytica.edulytica_api.app import app


@pytest.mark.asyncio
@patch("edulytica.edulytica_api.routers.account.UserCrud.update")
def test_edit_profile_success(mock_update, client):
    response = client(app).post("/account/edit_profile", json={
        "name": "John",
        "organization": "TestOrg"
    })
    assert response.status_code == status.HTTP_200_OK
    mock_update.assert_called_once()


@pytest.mark.asyncio
def test_edit_profile_none_fields(client):
    response = client(app).post("/account/edit_profile", json={})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "None of the arguments were specified"


@pytest.mark.asyncio
@patch("edulytica.edulytica_api.routers.account.UserCrud.update")
def test_change_password_success(mock_update, client):
    response = client(app).post("/account/change_password", json={
        "old_password": "testpassword",
        "new_password1": "newpass",
        "new_password2": "newpass"
    })

    assert response.status_code == status.HTTP_200_OK
    mock_update.assert_called_once()


@pytest.mark.asyncio
@patch("edulytica.edulytica_api.routers.account.verify_password")
def test_change_password_wrong_old(mock_verify, client):
    mock_verify.return_value = False

    response = client(app).post("/account/change_password", json={
        "old_password": "wrong",
        "new_password1": "new",
        "new_password2": "new"
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Old password incorrect"


@pytest.mark.asyncio
def test_change_password_mismatch(client):
    response = client(app).post("/account/change_password", json={
        "old_password": "testpassword",
        "new_password1": "new1",
        "new_password2": "new2"
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "New passwords not equal"


@pytest.mark.asyncio
@patch("edulytica.edulytica_api.routers.account.TicketCrud.get_filtered_by_params")
def test_ticket_history_success(mock_get_tickets, client):
    mock_get_tickets.return_value = [{"id": 1, "title": "Ticket A"}]

    response = client(app).get("/account/ticket_history")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Ticket history found"
    assert "tickets" in response.json()
    assert len(response.json()["tickets"]) == 1
