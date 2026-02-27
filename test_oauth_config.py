"""Unit tests for oauth_config module."""

import pytest
from unittest.mock import patch

from oauth_config import load_oauth_config, OAuthConfigError


GOOGLE_VARS = {
    "OAUTH_GOOGLE_CLIENT_ID": "google-id",
    "OAUTH_GOOGLE_CLIENT_SECRET": "google-secret",
    "OAUTH_GOOGLE_REDIRECT_URI": "http://localhost/auth/google/callback",
}

GITHUB_VARS = {
    "OAUTH_GITHUB_CLIENT_ID": "github-id",
    "OAUTH_GITHUB_CLIENT_SECRET": "github-secret",
    "OAUTH_GITHUB_REDIRECT_URI": "http://localhost/auth/github/callback",
}


def test_load_google_config(monkeypatch):
    for k, v in GOOGLE_VARS.items():
        monkeypatch.setenv(k, v)

    configs = load_oauth_config()
    assert "google" in configs
    cfg = configs["google"]
    assert cfg.client_id == "google-id"
    assert cfg.client_secret == "google-secret"
    assert cfg.redirect_uri == "http://localhost/auth/google/callback"
    assert cfg.provider == "google"


def test_load_github_config(monkeypatch):
    for k, v in GITHUB_VARS.items():
        monkeypatch.setenv(k, v)

    configs = load_oauth_config()
    assert "github" in configs
    cfg = configs["github"]
    assert cfg.client_id == "github-id"


def test_unconfigured_provider_not_returned(monkeypatch):
    # Ensure no OAuth env vars are set
    for key in list(GOOGLE_VARS) + list(GITHUB_VARS):
        monkeypatch.delenv(key, raising=False)

    configs = load_oauth_config()
    assert configs == {}


def test_partial_config_raises(monkeypatch):
    monkeypatch.setenv("OAUTH_GOOGLE_CLIENT_ID", "only-id")
    monkeypatch.delenv("OAUTH_GOOGLE_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("OAUTH_GOOGLE_REDIRECT_URI", raising=False)

    with pytest.raises(OAuthConfigError, match="Incomplete google"):
        load_oauth_config()


def test_require_providers_missing_raises(monkeypatch):
    for key in list(GOOGLE_VARS) + list(GITHUB_VARS):
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(OAuthConfigError, match="Required OAuth provider"):
        load_oauth_config(require_providers=["google"])


def test_require_providers_present_passes(monkeypatch):
    for k, v in GOOGLE_VARS.items():
        monkeypatch.setenv(k, v)

    configs = load_oauth_config(require_providers=["google"])
    assert "google" in configs
