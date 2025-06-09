import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock, mock_open
from src.edulytica_api.app import app


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.os.makedirs")
@patch("builtins.open", new_callable=mock_open)
@patch("src.edulytica_api.routers.actions.EventCrud.get_by_id")
@patch("src.edulytica_api.routers.actions.CustomEventCrud.get_by_id")
@patch("src.edulytica_api.routers.actions.DocumentCrud.get_by_id")
@patch("src.edulytica_api.routers.actions.DocumentCrud.create")
@patch("src.edulytica_api.routers.actions.TicketStatusCrud.get_filtered_by_params")
@patch("src.edulytica_api.routers.actions.TicketTypeCrud.get_filtered_by_params")
@patch("src.edulytica_api.routers.actions.TicketCrud.create")
@patch("src.edulytica_api.routers.actions.get_structural_paragraphs")
@patch("src.edulytica_api.routers.actions.Producer")
def test_new_ticket_success(
    mock_kafka_producer,
    mock_get_paragraphs,
    mock_ticket_create,
    mock_type,
    mock_status,
    mock_doc_create,
    mock_doc_get,
    mock_custom_event,
    mock_event,
    mock_file_open,
    mock_makedirs,
    client
):
    mock_event.return_value = AsyncMock(id=uuid.uuid4())
    mock_custom_event.return_value = None
    mock_doc_get.return_value = None
    mock_status.return_value = [AsyncMock(id=1)]
    mock_type.return_value = [AsyncMock(id=1)]
    mock_ticket_create.return_value = AsyncMock(id=123)

    mock_get_paragraphs.return_value = {
        "table_of_content": [{"text": ["Intro"]}],
        "other_text": ["Main"]
    }

    mock_producer_instance = MagicMock()
    mock_kafka_producer.return_value = mock_producer_instance

    file_content = b"dummy file content"
    response = client(app).post(
        "/actions/new_ticket",
        files={"file": ("test.pdf", file_content, "application/pdf")},
        data={"event_id": str(uuid.uuid4())}
    )

    assert response.status_code == 200
    assert "ticket_id" in response.json()

    mock_producer_instance.produce.assert_called_once()
    mock_producer_instance.flush.assert_called_once()


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.EventCrud.get_by_id")
@patch("src.edulytica_api.routers.actions.CustomEventCrud.get_by_id")
def test_new_ticket_invalid_event(mock_custom_event, mock_event, client):
    mock_event.return_value = None
    mock_custom_event.return_value = None

    file_content = b"dummy file content"
    response = client(app).post(
        "/actions/new_ticket",
        files={"file": ("test.pdf", file_content, "application/pdf")},
        data={"event_id": str(uuid.uuid4())}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect event id"


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.EventCrud.get_by_id")
@patch("src.edulytica_api.routers.actions.CustomEventCrud.get_by_id")
def test_new_ticket_invalid_file_type(mock_custom_event, mock_event, client):
    mock_event.return_value = AsyncMock(id=uuid.uuid4())
    mock_custom_event.return_value = None

    file_content = b"dummy file content"
    response = client(app).post(
        "/actions/new_ticket",
        files={"file": ("test.pdf", file_content, "application/epub+zip")},
        data={"event_id": str(uuid.uuid4())}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file type, only PDF or DOCX"


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.EventCrud.get_filtered_by_params")
@patch("src.edulytica_api.routers.actions.CustomEventCrud.get_filtered_by_params")
def test_get_event_id_success(mock_custom, mock_event, client):
    mock_event.return_value = None
    mock_custom.return_value = AsyncMock(id=uuid.uuid4())

    response = client(app).get("/actions/get_event_id", params={"event_name": "test"})
    assert response.status_code == 200
    assert "event_id" in response.json()


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.EventCrud.get_filtered_by_params")
@patch("src.edulytica_api.routers.actions.CustomEventCrud.get_filtered_by_params")
def test_get_event_id_not_found(mock_custom, mock_event, client):
    mock_event.return_value = None
    mock_custom.return_value = None

    response = client(app).get("/actions/get_event_id", params={"event_name": "nonexistent"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Event doesn't exist"


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.TicketCrud.get_ticket_by_id_or_shared")
def test_get_ticket_success(mock_get_ticket, client):
    mock_get_ticket.return_value = ["mock_ticket"]

    response = client(app).get("/actions/get_ticket", params={"ticket_id": str(uuid.uuid4())})
    assert response.status_code == 200
    assert response.json()["ticket"] == "mock_ticket"


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.TicketCrud.get_ticket_by_id_or_shared")
def test_get_ticket_not_found(mock_get_ticket, client):
    mock_get_ticket.return_value = []

    response = client(app).get("/actions/get_ticket", params={"ticket_id": str(uuid.uuid4())})
    assert response.status_code == 400
    assert response.json()["detail"]


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.TicketCrud.get_ticket_by_id_or_shared")
@patch("src.edulytica_api.routers.actions.DocumentCrud.get_by_id")
def test_get_ticket_file_success(mock_doc_get, mock_ticket_get, client, tmp_path):
    file_path = tmp_path / "test.pdf"
    file_path.write_text("dummy")

    mock_ticket_get.return_value = MagicMock(document_id=uuid.uuid4())
    mock_doc_get.return_value = MagicMock(file_path=str(file_path))

    response = client(app).get("/actions/get_ticket_file", params={"ticket_id": str(uuid.uuid4())})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.TicketCrud.get_ticket_by_id_or_shared")
def test_get_ticket_file_ticket_not_found(mock_ticket_get, client):
    mock_ticket_get.return_value = None

    response = client(app).get("/actions/get_ticket_file", params={"ticket_id": str(uuid.uuid4())})
    assert response.status_code == 400


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.TicketCrud.get_ticket_by_id_or_shared")
@patch("src.edulytica_api.routers.actions.DocumentSummaryCrud.get_by_id")
def test_get_ticket_summary_success(mock_summary, mock_ticket, client, tmp_path):
    file_path = tmp_path / "summary.txt"
    file_path.write_text("summary")

    mock_ticket.return_value = MagicMock(document_summary_id=uuid.uuid4())
    mock_summary.return_value = MagicMock(file_path=str(file_path))

    response = client(app).get(
        "/actions/get_ticket_summary",
        params={
            "ticket_id": str(
                uuid.uuid4())})
    assert response.status_code == 200


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.TicketCrud.get_ticket_by_id_or_shared")
def test_get_ticket_summary_not_found(mock_ticket, client):
    mock_ticket.return_value = None

    response = client(app).get(
        "/actions/get_ticket_summary",
        params={
            "ticket_id": str(
                uuid.uuid4())})
    assert response.status_code == 400


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.TicketCrud.get_ticket_by_id_or_shared")
@patch("src.edulytica_api.routers.actions.DocumentReportCrud.get_by_id")
def test_get_ticket_result_success(mock_report, mock_ticket, client, tmp_path):
    file_path = tmp_path / "result.txt"
    file_path.write_text("result")

    mock_ticket.return_value = MagicMock(document_id=uuid.uuid4())
    mock_report.return_value = MagicMock(file_path=str(file_path))

    response = client(app).get(
        "/actions/get_ticket_result",
        params={
            "ticket_id": str(
                uuid.uuid4())})
    assert response.status_code == 200


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.TicketCrud.get_ticket_by_id_or_shared")
def test_get_ticket_result_not_found(mock_ticket, client):
    mock_ticket.return_value = None

    response = client(app).get(
        "/actions/get_ticket_result",
        params={
            "ticket_id": str(
                uuid.uuid4())})
    assert response.status_code == 400


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.TicketCrud.get_filtered_by_params")
@patch("src.edulytica_api.routers.actions.TicketCrud.update")
def test_ticket_share_success(mock_update, mock_get, client):
    mock_get.return_value = MagicMock(shared=False)

    response = client(app).post("/actions/ticket_share", json={"ticket_id": str(uuid.uuid4())})
    assert response.status_code == 200
    assert response.json()["detail"] == "Status has been changed"


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.TicketCrud.get_filtered_by_params")
def test_ticket_share_not_found(mock_get, client):
    mock_get.return_value = []

    response = client(app).post("/actions/ticket_share", json={"ticket_id": str(uuid.uuid4())})
    assert response.status_code == 400
    assert response.json()["detail"] == "You aren't ticket owner or ticket doesn't exist"
