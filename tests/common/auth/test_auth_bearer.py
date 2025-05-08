import pytest
from jose import jwt
from fastapi import HTTPException
from src.common.auth.auth_bearer import AuthDataGetterFromToken
from src.common.auth.helpers.utils import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from src.common.config import JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY, ALGORITHM


class FakeUser:
    def __init__(self, is_active=True):
        self.is_active = is_active


@pytest.fixture
def valid_payload():
    return {
        "sub": "user123",
        "token_type": ACCESS_TOKEN_TYPE
    }


@pytest.fixture
def valid_token(valid_payload):
    return jwt.encode(valid_payload, JWT_SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def refresh_payload():
    return {
        "sub": "user123",
        "token_type": REFRESH_TOKEN_TYPE
    }


@pytest.fixture
def refresh_token(refresh_payload):
    return jwt.encode(refresh_payload, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)


@pytest.mark.asyncio
async def test_access_token_auth_success(mocker, valid_token, valid_payload):
    mock_session = mocker.MagicMock()

    mocker.patch(
        "src.common.auth.auth_bearer.UserCrud.get_by_id",
        return_value=FakeUser()
    )

    auth = AuthDataGetterFromToken(token_type=ACCESS_TOKEN_TYPE, secret_key=JWT_SECRET_KEY)
    result = await auth(token=valid_token, session=mock_session)

    assert result["payload"]["sub"] == "user123"
    assert result["user"].is_active
    assert result["token"] == valid_token


@pytest.mark.asyncio
async def test_access_token_invalid_type(mocker, valid_token):
    mock_session = mocker.MagicMock()

    auth = AuthDataGetterFromToken(token_type=REFRESH_TOKEN_TYPE, secret_key=JWT_SECRET_KEY)

    with pytest.raises(HTTPException) as exc_info:
        await auth(token=valid_token, session=mock_session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate token type"


@pytest.mark.asyncio
async def test_invalid_jwt_raises_credentials_exception(mocker):
    mock_session = mocker.MagicMock()
    invalid_token = "invalid.token.parts"

    auth = AuthDataGetterFromToken(token_type=ACCESS_TOKEN_TYPE, secret_key=JWT_SECRET_KEY)

    with pytest.raises(HTTPException) as exc_info:
        await auth(token=invalid_token, session=mock_session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_user_not_found_raises_credentials_exception(mocker, valid_token, valid_payload):
    mock_session = mocker.MagicMock()

    mocker.patch(
        "src.common.auth.auth_bearer.UserCrud.get_by_id",
        return_value=None
    )

    auth = AuthDataGetterFromToken(token_type=ACCESS_TOKEN_TYPE, secret_key=JWT_SECRET_KEY)

    with pytest.raises(HTTPException) as exc_info:
        await auth(token=valid_token, session=mock_session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_user_inactive_raises_bad_request(mocker, valid_token, valid_payload):
    mock_session = mocker.MagicMock()

    mocker.patch(
        "src.common.auth.auth_bearer.UserCrud.get_by_id",
        return_value=FakeUser(is_active=False)
    )

    auth = AuthDataGetterFromToken(token_type=ACCESS_TOKEN_TYPE, secret_key=JWT_SECRET_KEY)

    with pytest.raises(HTTPException) as exc_info:
        await auth(token=valid_token, session=mock_session)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Inactive user"
