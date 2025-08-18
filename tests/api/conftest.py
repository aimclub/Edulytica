from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, Response

from edulytica.auth.app import app
from edulytica.common.auth.auth_bearer import refresh_token_auth, access_token_auth
from edulytica.common.auth.helpers.utils import get_hashed_password
from edulytica.common.database.database import get_session, SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession

from edulytica.edulytica_api.dependencies import get_http_client


async def override_get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@pytest.fixture
def mock_http_client():
    mock_client = AsyncMock(spec=AsyncClient)
    mock_response = Response(200)
    mock_response._content = b'{"status": "ok"}'
    mock_client.post = AsyncMock(return_value=mock_response)
    return mock_client


@pytest.fixture
def client(mock_http_client):
    def _client_for_app(app):
        app.dependency_overrides[get_session] = override_get_session

        async def mock_refresh_token_auth():
            class DummyUser:
                id = 1
                is_active = True

            return {
                "user": DummyUser(),
                "token": "mocked-token",
                "payload": {"checker": "mocked-checker"}
            }

        app.dependency_overrides[refresh_token_auth] = mock_refresh_token_auth

        async def mock_access_token_auth():
            class DummyUser:
                id = 1
                is_active = True
                password_hash = get_hashed_password('testpassword')

            return {
                "user": DummyUser(),
                "token": "mocked-token",
                "payload": {"payload": "JustPayload"}
            }

        app.dependency_overrides[access_token_auth] = mock_access_token_auth
        app.dependency_overrides[get_http_client] = lambda: mock_http_client

        return TestClient(app)
    return _client_for_app


@pytest.fixture(scope="session")
def integration_client():
    with TestClient(app) as c:
        yield c
