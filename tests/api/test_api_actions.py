import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock, mock_open
from starlette.status import HTTP_202_ACCEPTED
from src.edulytica_api.app import app


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.fast_parse_text")
@patch("src.edulytica_api.routers.actions.TicketCrud.create")
@patch("src.edulytica_api.routers.actions.TicketTypeCrud.get_filtered_by_params")
@patch("src.edulytica_api.routers.actions.TicketStatusCrud.get_filtered_by_params")
@patch("src.edulytica_api.routers.actions.DocumentCrud.create")
@patch("src.edulytica_api.routers.actions.DocumentCrud.get_by_id")
@patch("src.edulytica_api.routers.actions.CustomEventCrud.get_by_id")
@patch("src.edulytica_api.routers.actions.EventCrud.get_by_id")
@patch("builtins.open", new_callable=mock_open)
@patch("src.edulytica_api.routers.actions.os.makedirs")
def test_new_ticket_success(
        mock_makedirs,
        mock_open_file,
        mock_event_get,
        mock_custom_event_get,
        mock_doc_get,
        mock_doc_create,
        mock_status,
        mock_type,
        mock_ticket_create,
        mock_parse_text,
        client,
        mock_http_client
):
    mock_event_get.return_value = MagicMock(id=uuid.uuid4())
    mock_custom_event_get.return_value = None
    mock_doc_get.return_value = None
    mock_status.return_value = [MagicMock(id=uuid.uuid4())]
    mock_type.return_value = [MagicMock(id=uuid.uuid4())]
    mock_ticket_create.return_value = MagicMock(id=uuid.uuid4())
    mock_parse_text.return_value = "some parsed text"
    mock_http_client.post = AsyncMock()
    mock_response = AsyncMock()
    mock_response.raise_for_status = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = '{"status": "ok"}'
    mock_http_client.post.return_value = mock_response

    file_data = b"dummy file content"
    files = {
        "file": (
            "test.docx",
            file_data,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    data = {
        "event_id": str(uuid.uuid4()),
        "mega_task_id": "1",
    }

    response = client(app).post(
        "/actions/new_ticket",
        data=data,
        files=files
    )

    assert response.status_code == HTTP_202_ACCEPTED
    assert "ticket_id" in response.json()
    mock_http_client.post.assert_awaited_once()


@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.EventCrud.get_by_id")
@patch("src.edulytica_api.routers.actions.CustomEventCrud.get_by_id")
def test_new_ticket_invalid_event(
    mock_custom_event_get,
    mock_event_get,
    client,
    mock_http_client
):
    mock_event_get.return_value = None
    mock_custom_event_get.return_value = None

    files = {
        "file": (
            "test.docx",
            b"content",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    data = {"event_id": str(uuid.uuid4()), "mega_task_id": "1"}

    response = client(app).post(
        "/actions/new_ticket",
        data=data,
        files=files
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect event id"


@pytest.mark.asyncio
@pytest.mark.asyncio
@patch("src.edulytica_api.routers.actions.EventCrud.get_by_id")
def test_new_ticket_invalid_file_type(
    mock_event_get,
    client,
    mock_http_client
):
    mock_event_get.return_value = MagicMock(id=uuid.uuid4())

    files = {"file": ("test.txt", b"content", "text/plain")}
    data = {"event_id": str(uuid.uuid4()), "mega_task_id": "1"}

    response = client(app).post(
        "/actions/new_ticket",
        data=data,
        files=files
    )

    assert response.status_code == 400
    assert response.json()["detail"] == 'Invalid file type, only PDF or DOCX'


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
    mock_get_ticket.return_value = "mock_ticket"

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
