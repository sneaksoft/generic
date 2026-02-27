"""Authentication dependency for FastAPI protected routes.

Extracts and validates JWT from the Authorization header (Bearer scheme),
attaching the decoded user ID to the request context via dependency injection.
"""

from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.token_service import TokenError, verify_token

# auto_error=False so we can return 401 instead of FastAPI's default 403
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_id(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> int:
    """Validate Bearer JWT and return the authenticated user ID.

    Attaches the user_id to request.state.user_id for downstream access.
    Raises HTTP 401 if the token is missing, invalid, or expired.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = verify_token(credentials.credentials)
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    request.state.user_id = user_id
    return user_id
