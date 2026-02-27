"""Unit tests for authentication middleware dependency."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.auth import get_current_user_id
from app.token_service import TokenError


def _make_request():
    """Create a minimal mock Request with a state attribute."""
    request = MagicMock()
    request.state = MagicMock()
    return request


def test_valid_token_returns_user_id():
    request = _make_request()
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.token.here")

    with patch("app.auth.verify_token", return_value=42):
        user_id = get_current_user_id(request, credentials)

    assert user_id == 42


def test_valid_token_attaches_user_id_to_request_state():
    request = _make_request()
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.token.here")

    with patch("app.auth.verify_token", return_value=7):
        get_current_user_id(request, credentials)

    assert request.state.user_id == 7


def test_missing_credentials_raises_401():
    request = _make_request()

    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(request, credentials=None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"


def test_invalid_token_raises_401():
    request = _make_request()
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad.token")

    with patch("app.auth.verify_token", side_effect=TokenError("Invalid token: ...")):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_id(request, credentials)

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"


def test_expired_token_raises_401():
    request = _make_request()
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="expired.token")

    with patch("app.auth.verify_token", side_effect=TokenError("Token has expired")):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_id(request, credentials)

    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()
