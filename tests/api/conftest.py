import pytest
from fastapi.testclient import TestClient
from src.auth.app import app
from src.common.auth.auth_bearer import refresh_token_auth
from src.common.database.database import get_session, SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


# 🎯 Переопределение зависимости
async def override_get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@pytest.fixture(scope="session", autouse=True)
def setup_overrides():
    app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(scope="function")
def override_refresh_token_auth():
    async def mock_refresh_dep():
        class DummyUser:
            id = 1
            is_active = True
        return {
            "user": DummyUser(),
            "token": "mocked-token",
            "payload": {"checker": "mocked-checker"}
        }

    app.dependency_overrides[refresh_token_auth] = mock_refresh_dep
    yield
    app.dependency_overrides.pop(refresh_token_auth, None)

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as client:
        yield client
