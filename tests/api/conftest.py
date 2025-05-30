import pytest
from fastapi.testclient import TestClient

from src.auth.app import app
from src.common.auth.auth_bearer import refresh_token_auth, access_token_auth
from src.common.auth.helpers.utils import get_hashed_password
from src.common.database.database import get_session, SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession


async def override_get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@pytest.fixture
def client():
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

        return TestClient(app)
    return _client_for_app


@pytest.fixture(scope="session")
def integration_client():
    with TestClient(app) as c:
        yield c
