"""OAuth authorization endpoints.

Provides:
  GET /auth/oauth/<provider>           - Redirect user to provider's authorization URL
  GET /auth/oauth/<provider>/callback  - Handle OAuth callback, exchange code for tokens,
                                         fetch user profile
"""

import secrets
import urllib.parse

import requests
from flask import Blueprint, abort, jsonify, redirect, request, session

from oauth_config import OAuthConfigError, load_oauth_config

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Provider-specific OAuth endpoints and scopes
PROVIDER_OAUTH_PARAMS = {
    "google": {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scope": "openid email profile",
    },
    "github": {
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "scope": "user:email",
    },
}


@auth_bp.route("/oauth/<provider>")
def oauth_initiate(provider):
    """Redirect the user to the OAuth provider's authorization URL.

    Generates a random CSRF state token stored in the session, then
    constructs and redirects to the provider's authorization URL with
    the appropriate scopes.
    """
    if provider not in PROVIDER_OAUTH_PARAMS:
        abort(404, description=f"Unsupported OAuth provider: {provider}")

    try:
        configs = load_oauth_config()
    except OAuthConfigError as e:
        abort(500, description=str(e))

    if provider not in configs:
        abort(404, description=f"OAuth provider not configured: {provider}")

    config = configs[provider]
    provider_params = PROVIDER_OAUTH_PARAMS[provider]

    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    session["oauth_provider"] = provider

    params = {
        "client_id": config.client_id,
        "redirect_uri": config.redirect_uri,
        "response_type": "code",
        "scope": provider_params["scope"],
        "state": state,
    }

    auth_url = provider_params["auth_url"] + "?" + urllib.parse.urlencode(params)
    return redirect(auth_url)


@auth_bp.route("/oauth/<provider>/callback")
def oauth_callback(provider):
    """Receive OAuth callback, exchange authorization code for tokens, fetch user profile.

    Validates the CSRF state parameter, exchanges the authorization code for
    access tokens, and retrieves the user's profile from the provider.
    """
    # Validate CSRF state
    state = request.args.get("state")
    expected_state = session.pop("oauth_state", None)
    session.pop("oauth_provider", None)

    if not state or state != expected_state:
        abort(400, description="Invalid or missing CSRF state parameter")

    # Check for OAuth error response from provider
    error = request.args.get("error")
    if error:
        error_description = request.args.get("error_description", error)
        abort(400, description=f"OAuth error: {error_description}")

    code = request.args.get("code")
    if not code:
        abort(400, description="Missing authorization code")

    if provider not in PROVIDER_OAUTH_PARAMS:
        abort(404, description=f"Unsupported OAuth provider: {provider}")

    try:
        configs = load_oauth_config()
    except OAuthConfigError as e:
        abort(500, description=str(e))

    if provider not in configs:
        abort(404, description=f"OAuth provider not configured: {provider}")

    config = configs[provider]
    provider_params = PROVIDER_OAUTH_PARAMS[provider]

    # Exchange authorization code for tokens
    token_response = requests.post(
        provider_params["token_url"],
        data={
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code": code,
            "redirect_uri": config.redirect_uri,
            "grant_type": "authorization_code",
        },
        headers={"Accept": "application/json"},
        timeout=10,
    )

    if not token_response.ok:
        abort(502, description="Failed to exchange authorization code for tokens")

    tokens = token_response.json()
    access_token = tokens.get("access_token")
    if not access_token:
        abort(502, description="No access token in provider response")

    # Fetch user profile from provider
    profile_response = requests.get(
        provider_params["userinfo_url"],
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )

    if not profile_response.ok:
        abort(502, description="Failed to fetch user profile from provider")

    user_profile = profile_response.json()

    return jsonify({"provider": provider, "profile": user_profile})
