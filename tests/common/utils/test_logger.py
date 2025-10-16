import pytest
import logging
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.common.utils.logger import api_logs


@pytest.fixture
def test_app():
    app = FastAPI()

    @api_logs(app.get("/test"))
    async def test_endpoint(name: str):
        return {"message": f"Hello {name}"}

    @api_logs(app.get("/error"))
    async def error_endpoint(name: str):
        raise ValueError("Something went wrong!")

    return app


@pytest.fixture
def client(test_app):
    return TestClient(test_app, raise_server_exceptions=False)


def test_api_logs_success(client, caplog):
    caplog.set_level(logging.DEBUG)

    response = client.get("/test", params={"name": "World"})

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

    log_messages = [record.getMessage() for record in caplog.records]

    assert any("Handler: test_endpoint" in message for message in log_messages)
    assert any("Params" in message for message in log_messages)
    assert any("TIME:" in message for message in log_messages)
    assert any("----------------------------" in message for message in log_messages)


def test_api_logs_error(client, caplog):
    caplog.set_level(logging.DEBUG)

    response = client.get("/error", params={"name": "World"})

    assert response.status_code == 500

    log_messages = [record.getMessage() for record in caplog.records]

    assert any("Exception: Something went wrong!" in message for message in log_messages)
    assert any("Handler: error_endpoint" in message for message in log_messages)
