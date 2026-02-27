"""Unit tests for OAuth authorization endpoints."""

import pytest
from unittest.mock import MagicMock, patch

from app import create_app

GOOGLE_ENV = {
    "OAUTH_GOOGLE_CLIENT_ID": "google-client-id",
    "OAUTH_GOOGLE_CLIENT_SECRET": "google-client-secret",
    "OAUTH_GOOGLE_REDIRECT_URI": "http://localhost:8000/auth/oauth/google/callback",
}

GITHUB_ENV = {
    "OAUTH_GITHUB_CLIENT_ID": "github-client-id",
    "OAUTH_GITHUB_CLIENT_SECRET": "github-client-secret",
    "OAUTH_GITHUB_REDIRECT_URI": "http://localhost:8000/auth/oauth/github/callback",
}


@pytest.fixture
def app():
    application = create_app()
    application.config["TESTING"] = True
    application.config["SECRET_KEY"] = "test-secret"
    return application


@pytest.fixture
def client(app):
    return app.test_client()


class TestOAuthInitiate:
    def test_redirects_to_google_auth_url(self, client, monkeypatch):
        for k, v in GOOGLE_ENV.items():
            monkeypatch.setenv(k, v)

        response = client.get("/auth/oauth/google")

        assert response.status_code == 302
        location = response.headers["Location"]
        assert "accounts.google.com" in location
        assert "client_id=google-client-id" in location
        assert "response_type=code" in location
        assert "scope=" in location
        assert "state=" in location

    def test_redirects_to_github_auth_url(self, client, monkeypatch):
        for k, v in GITHUB_ENV.items():
            monkeypatch.setenv(k, v)

        response = client.get("/auth/oauth/github")

        assert response.status_code == 302
        location = response.headers["Location"]
        assert "github.com/login/oauth/authorize" in location
        assert "client_id=github-client-id" in location
        assert "state=" in location

    def test_state_stored_in_session(self, client, monkeypatch):
        for k, v in GOOGLE_ENV.items():
            monkeypatch.setenv(k, v)

        with client.session_transaction() as sess:
            sess.clear()

        client.get("/auth/oauth/google")

        with client.session_transaction() as sess:
            assert "oauth_state" in sess
            assert len(sess["oauth_state"]) > 0
            assert sess["oauth_provider"] == "google"

    def test_unknown_provider_returns_404(self, client):
        response = client.get("/auth/oauth/twitter")
        assert response.status_code == 404

    def test_unconfigured_provider_returns_404(self, client, monkeypatch):
        # Ensure no Google env vars set
        for k in GOOGLE_ENV:
            monkeypatch.delenv(k, raising=False)
        for k in GITHUB_ENV:
            monkeypatch.delenv(k, raising=False)

        response = client.get("/auth/oauth/google")
        assert response.status_code == 404


class TestOAuthCallback:
    def _set_session_state(self, client, state, provider):
        with client.session_transaction() as sess:
            sess["oauth_state"] = state
            sess["oauth_provider"] = provider

    def test_invalid_state_returns_400(self, client, monkeypatch):
        for k, v in GOOGLE_ENV.items():
            monkeypatch.setenv(k, v)

        self._set_session_state(client, "expected-state", "google")
        response = client.get("/auth/oauth/google/callback?code=authcode&state=wrong-state")

        assert response.status_code == 400

    def test_missing_state_returns_400(self, client, monkeypatch):
        for k, v in GOOGLE_ENV.items():
            monkeypatch.setenv(k, v)

        self._set_session_state(client, "expected-state", "google")
        response = client.get("/auth/oauth/google/callback?code=authcode")

        assert response.status_code == 400

    def test_oauth_error_from_provider_returns_400(self, client, monkeypatch):
        for k, v in GOOGLE_ENV.items():
            monkeypatch.setenv(k, v)

        self._set_session_state(client, "abc123", "google")
        response = client.get(
            "/auth/oauth/google/callback?error=access_denied&state=abc123"
        )

        assert response.status_code == 400

    def test_missing_code_returns_400(self, client, monkeypatch):
        for k, v in GOOGLE_ENV.items():
            monkeypatch.setenv(k, v)

        self._set_session_state(client, "abc123", "google")
        response = client.get("/auth/oauth/google/callback?state=abc123")

        assert response.status_code == 400

    def test_successful_callback_returns_profile(self, client, monkeypatch):
        for k, v in GOOGLE_ENV.items():
            monkeypatch.setenv(k, v)

        self._set_session_state(client, "valid-state", "google")

        mock_token_response = MagicMock()
        mock_token_response.ok = True
        mock_token_response.json.return_value = {"access_token": "tok123"}

        mock_profile_response = MagicMock()
        mock_profile_response.ok = True
        mock_profile_response.json.return_value = {"id": "user1", "email": "user@example.com"}

        with patch("auth_routes.requests.post", return_value=mock_token_response), \
             patch("auth_routes.requests.get", return_value=mock_profile_response):
            response = client.get(
                "/auth/oauth/google/callback?code=authcode&state=valid-state"
            )

        assert response.status_code == 200
        data = response.get_json()
        assert data["provider"] == "google"
        assert data["profile"]["email"] == "user@example.com"

    def test_token_exchange_failure_returns_502(self, client, monkeypatch):
        for k, v in GOOGLE_ENV.items():
            monkeypatch.setenv(k, v)

        self._set_session_state(client, "valid-state", "google")

        mock_token_response = MagicMock()
        mock_token_response.ok = False

        with patch("auth_routes.requests.post", return_value=mock_token_response):
            response = client.get(
                "/auth/oauth/google/callback?code=authcode&state=valid-state"
            )

        assert response.status_code == 502

    def test_profile_fetch_failure_returns_502(self, client, monkeypatch):
        for k, v in GOOGLE_ENV.items():
            monkeypatch.setenv(k, v)

        self._set_session_state(client, "valid-state", "google")

        mock_token_response = MagicMock()
        mock_token_response.ok = True
        mock_token_response.json.return_value = {"access_token": "tok123"}

        mock_profile_response = MagicMock()
        mock_profile_response.ok = False

        with patch("auth_routes.requests.post", return_value=mock_token_response), \
             patch("auth_routes.requests.get", return_value=mock_profile_response):
            response = client.get(
                "/auth/oauth/google/callback?code=authcode&state=valid-state"
            )

        assert response.status_code == 502

    def test_unknown_provider_in_callback_returns_404(self, client):
        with client.session_transaction() as sess:
            sess["oauth_state"] = "abc"
            sess["oauth_provider"] = "twitter"

        response = client.get("/auth/oauth/twitter/callback?code=x&state=abc")
        assert response.status_code == 404
