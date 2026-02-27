"""Unit tests for local registration and login/logout endpoints."""

import importlib.util
import os
from unittest.mock import MagicMock, patch

import pytest

# Load root-level app.py (shadowed by app/ package when using normal imports)
_spec = importlib.util.spec_from_file_location(
    "flask_app", os.path.join(os.path.dirname(__file__), "../app.py")
)
_flask_app_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_flask_app_module)
create_app = _flask_app_module.create_app


@pytest.fixture
def app():
    application = create_app()
    application.config["TESTING"] = True
    application.config["SECRET_KEY"] = "test-secret"
    return application


@pytest.fixture
def client(app):
    return app.test_client()


class TestRegister:
    def test_register_success_returns_201_with_token(self, client):
        mock_user = MagicMock()
        mock_user.id = 1

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        def mock_refresh(user):
            user.id = 1

        mock_db.refresh.side_effect = mock_refresh

        with patch("auth_routes.SessionLocal", return_value=mock_db), \
             patch("auth_routes.bcrypt.hashpw", return_value=b"$2b$12$hashedpassword"), \
             patch("auth_routes.bcrypt.gensalt", return_value=b"$2b$12$salt"), \
             patch("auth_routes.create_access_token", return_value="test.jwt.token"):
            response = client.post(
                "/auth/register",
                json={"email": "user@example.com", "password": "secret123"},
            )

        assert response.status_code == 201
        data = response.get_json()
        assert data["access_token"] == "test.jwt.token"
        assert data["token_type"] == "bearer"

    def test_register_duplicate_email_returns_409(self, client):
        existing_user = MagicMock()

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user

        with patch("auth_routes.SessionLocal", return_value=mock_db), \
             patch("auth_routes.bcrypt.hashpw", return_value=b"$2b$12$hashedpassword"), \
             patch("auth_routes.bcrypt.gensalt", return_value=b"$2b$12$salt"):
            response = client.post(
                "/auth/register",
                json={"email": "user@example.com", "password": "secret123"},
            )

        assert response.status_code == 409

    def test_register_missing_email_returns_400(self, client):
        response = client.post("/auth/register", json={"password": "secret123"})
        assert response.status_code == 400

    def test_register_missing_password_returns_400(self, client):
        response = client.post("/auth/register", json={"email": "user@example.com"})
        assert response.status_code == 400

    def test_register_non_json_body_returns_4xx(self, client):
        response = client.post("/auth/register", data="not json", content_type="text/plain")
        assert 400 <= response.status_code < 500

    def test_register_normalizes_email_to_lowercase(self, client):
        captured_user = {}

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        def capture_add(user):
            captured_user["email"] = user.email

        mock_db.add.side_effect = capture_add

        def mock_refresh(user):
            user.id = 1

        mock_db.refresh.side_effect = mock_refresh

        with patch("auth_routes.SessionLocal", return_value=mock_db), \
             patch("auth_routes.bcrypt.hashpw", return_value=b"$2b$12$hashedpassword"), \
             patch("auth_routes.bcrypt.gensalt", return_value=b"$2b$12$salt"), \
             patch("auth_routes.create_access_token", return_value="token"):
            client.post(
                "/auth/register",
                json={"email": "User@Example.COM", "password": "secret123"},
            )

        assert captured_user["email"] == "user@example.com"


class TestLogin:
    def test_login_success_returns_token(self, client):
        mock_user = MagicMock()
        mock_user.id = 5
        mock_user.hashed_password = "$2b$12$hashedpassword"

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        with patch("auth_routes.SessionLocal", return_value=mock_db), \
             patch("auth_routes.bcrypt.checkpw", return_value=True), \
             patch("auth_routes.create_access_token", return_value="login.jwt.token"):
            response = client.post(
                "/auth/login",
                json={"email": "user@example.com", "password": "secret123"},
            )

        assert response.status_code == 200
        data = response.get_json()
        assert data["access_token"] == "login.jwt.token"
        assert data["token_type"] == "bearer"

    def test_login_wrong_password_returns_401(self, client):
        mock_user = MagicMock()
        mock_user.id = 5
        mock_user.hashed_password = "$2b$12$hashedpassword"

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        with patch("auth_routes.SessionLocal", return_value=mock_db), \
             patch("auth_routes.bcrypt.checkpw", return_value=False):
            response = client.post(
                "/auth/login",
                json={"email": "user@example.com", "password": "wrongpassword"},
            )

        assert response.status_code == 401

    def test_login_unknown_email_returns_401(self, client):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        with patch("auth_routes.SessionLocal", return_value=mock_db):
            response = client.post(
                "/auth/login",
                json={"email": "nobody@example.com", "password": "secret123"},
            )

        assert response.status_code == 401

    def test_login_missing_email_returns_400(self, client):
        response = client.post("/auth/login", json={"password": "secret123"})
        assert response.status_code == 400

    def test_login_missing_password_returns_400(self, client):
        response = client.post("/auth/login", json={"email": "user@example.com"})
        assert response.status_code == 400

    def test_login_non_json_body_returns_4xx(self, client):
        response = client.post("/auth/login", data="not json", content_type="text/plain")
        assert 400 <= response.status_code < 500

    def test_login_oauth_user_without_password_returns_401(self, client):
        mock_user = MagicMock()
        mock_user.hashed_password = None

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        with patch("auth_routes.SessionLocal", return_value=mock_db):
            response = client.post(
                "/auth/login",
                json={"email": "oauth@example.com", "password": "secret123"},
            )

        assert response.status_code == 401


class TestLogout:
    def test_logout_success_returns_200(self, client):
        with patch("auth_routes.verify_token", return_value=1), \
             patch("auth_routes.revoke_token") as mock_revoke:
            response = client.post(
                "/auth/logout",
                headers={"Authorization": "Bearer valid.jwt.token"},
            )

        assert response.status_code == 200
        mock_revoke.assert_called_once_with("valid.jwt.token")
        data = response.get_json()
        assert "logged out" in data["message"].lower()

    def test_logout_missing_auth_header_returns_401(self, client):
        response = client.post("/auth/logout")
        assert response.status_code == 401

    def test_logout_invalid_token_returns_401(self, client):
        from app.token_service import TokenError

        with patch("auth_routes.verify_token", side_effect=TokenError("Invalid token")):
            response = client.post(
                "/auth/logout",
                headers={"Authorization": "Bearer bad.token"},
            )

        assert response.status_code == 401

    def test_logout_non_bearer_scheme_returns_401(self, client):
        response = client.post(
            "/auth/logout",
            headers={"Authorization": "Basic dXNlcjpwYXNz"},
        )
        assert response.status_code == 401
