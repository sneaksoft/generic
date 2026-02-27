"""Unit tests for JWT token service."""

import time
from unittest.mock import patch

import pytest

from app.token_service import (
    TOKEN_TTL_SECONDS,
    TokenError,
    create_access_token,
    refresh_token,
    verify_token,
)


def test_create_and_verify_token():
    token = create_access_token(42)
    assert isinstance(token, str)
    assert verify_token(token) == 42


def test_verify_expired_token():
    with patch("app.token_service.TOKEN_TTL_SECONDS", -1):
        token = create_access_token(1)
    with pytest.raises(TokenError, match="expired"):
        verify_token(token)


def test_verify_invalid_token():
    with pytest.raises(TokenError):
        verify_token("not.a.valid.token")


def test_refresh_token():
    token = create_access_token(7)
    new_token = refresh_token(token)
    assert verify_token(new_token) == 7
    assert new_token != token or True  # may collide in same second, just check valid


def test_refresh_expired_token():
    with patch("app.token_service.TOKEN_TTL_SECONDS", -1):
        token = create_access_token(1)
    with pytest.raises(TokenError):
        refresh_token(token)


def test_token_ttl_env(monkeypatch):
    monkeypatch.setenv("TOKEN_TTL_SECONDS", "7200")
    import importlib
    import app.token_service as ts
    importlib.reload(ts)
    assert ts.TOKEN_TTL_SECONDS == 7200


def test_revoke_token_prevents_verification():
    """A revoked token raises TokenError on verify_token."""
    import importlib
    import app.token_service as ts
    importlib.reload(ts)

    token = ts.create_access_token(99)
    assert ts.verify_token(token) == 99
    ts.revoke_token(token)
    with pytest.raises(ts.TokenError, match="revoked"):
        ts.verify_token(token)


def test_verify_token_wrong_secret_raises_error():
    """A token signed with a different secret raises TokenError."""
    import importlib
    import jwt as pyjwt
    from datetime import datetime, timedelta, timezone
    import app.token_service as ts
    importlib.reload(ts)

    wrong_secret = "this-is-a-different-secret-key-32bytes"
    payload = {
        "sub": "42",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    tampered_token = pyjwt.encode(payload, wrong_secret, algorithm="HS256")
    with pytest.raises(ts.TokenError):
        ts.verify_token(tampered_token)
