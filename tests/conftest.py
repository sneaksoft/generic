"""Shared pytest fixtures and setup for the tests/ directory."""

import pytest


@pytest.fixture(autouse=True)
def resync_auth_routes_with_token_service():
    """Resync auth_routes module-level imports after each test.

    Some tests reload app.token_service (e.g. to pick up env var changes),
    which creates new class objects.  auth_routes.py captured the old objects
    at import time, so after a reload its TokenError / verify_token references
    become stale.  Running this fixture after every test keeps them in sync
    and prevents cross-test interference.
    """
    yield
    try:
        import app.token_service as ts
        import auth_routes

        auth_routes.TokenError = ts.TokenError
        auth_routes.verify_token = ts.verify_token
        auth_routes.revoke_token = ts.revoke_token
        auth_routes.create_access_token = ts.create_access_token
    except Exception:
        pass
