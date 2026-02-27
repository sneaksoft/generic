"""JWT token service for issuing and validating access tokens.

Used by both local and OAuth login flows.
"""

import os
from datetime import datetime, timedelta, timezone

import jwt

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "changeme-secret-key")
ALGORITHM = "HS256"
TOKEN_TTL_SECONDS = int(os.environ.get("TOKEN_TTL_SECONDS", "3600"))

_revoked_tokens: set[str] = set()


class TokenError(Exception):
    """Raised when token validation fails."""


def create_access_token(user_id: int) -> str:
    """Sign a JWT containing the user ID and expiration."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=TOKEN_TTL_SECONDS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> int:
    """Verify a JWT and return the user ID.

    Raises TokenError if the token is invalid or expired.
    """
    if token in _revoked_tokens:
        raise TokenError("Token has been revoked")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise TokenError("Token has expired")
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise TokenError(f"Invalid token: {exc}")


def revoke_token(token: str) -> None:
    """Add a token to the revocation list, preventing future use."""
    _revoked_tokens.add(token)


def refresh_token(token: str) -> str:
    """Issue a new token given a still-valid existing token.

    Raises TokenError if the existing token is invalid.
    """
    user_id = verify_token(token)
    return create_access_token(user_id)
