"""Unit tests for the User model."""

from datetime import datetime

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.database import Base
from app.models.user import User


@pytest.fixture
def engine():
    """In-memory SQLite engine for isolated tests."""
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture
def db_session(engine):
    """Database session bound to in-memory engine."""
    with Session(engine) as session:
        yield session


class TestUserModelFields:
    def test_table_name(self):
        assert User.__tablename__ == "users"

    def test_all_columns_exist(self, engine):
        inspector = inspect(engine)
        columns = {col["name"] for col in inspector.get_columns("users")}
        expected = {
            "id",
            "email",
            "hashed_password",
            "oauth_provider_id",
            "oauth_provider_name",
            "oauth_access_token",
            "oauth_refresh_token",
            "created_at",
            "updated_at",
        }
        assert expected == columns

    def test_email_column_is_unique(self, engine):
        inspector = inspect(engine)
        indexes = inspector.get_indexes("users")
        unique_indexes = [idx for idx in indexes if idx["unique"]]
        indexed_cols = [col for idx in unique_indexes for col in idx["column_names"]]
        assert "email" in indexed_cols


class TestLocalUserCreation:
    def test_create_local_user(self, db_session):
        user = User(email="alice@example.com", hashed_password="hashed_pw_123")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "alice@example.com"
        assert user.hashed_password == "hashed_pw_123"
        assert user.oauth_provider_id is None
        assert user.oauth_provider_name is None
        assert user.oauth_access_token is None
        assert user.oauth_refresh_token is None

    def test_local_user_timestamps_set_on_create(self, db_session):
        user = User(email="bob@example.com", hashed_password="pw")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)


class TestOAuthUserCreation:
    def test_create_oauth_user(self, db_session):
        user = User(
            email="carol@example.com",
            oauth_provider_id="google-uid-9876",
            oauth_provider_name="google",
            oauth_access_token="access_token_abc",
            oauth_refresh_token="refresh_token_xyz",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "carol@example.com"
        assert user.hashed_password is None
        assert user.oauth_provider_id == "google-uid-9876"
        assert user.oauth_provider_name == "google"
        assert user.oauth_access_token == "access_token_abc"
        assert user.oauth_refresh_token == "refresh_token_xyz"

    def test_oauth_user_timestamps_set_on_create(self, db_session):
        user = User(
            email="dave@example.com",
            oauth_provider_id="gh-111",
            oauth_provider_name="github",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)


class TestUserRepr:
    def test_repr_local_user(self):
        user = User(email="eve@example.com", hashed_password="pw")
        assert "local" in repr(user)
        assert "eve@example.com" in repr(user)

    def test_repr_oauth_user(self):
        user = User(
            email="frank@example.com",
            oauth_provider_name="google",
            oauth_provider_id="google-123",
        )
        assert "oauth" in repr(user)
        assert "frank@example.com" in repr(user)
