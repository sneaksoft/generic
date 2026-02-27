# OAuth Provider Setup

This document describes how to register the application with OAuth providers
and configure the required credentials.

## Environment Variables

Copy `.env.example` to `.env` and populate the values:

```
cp .env.example .env
```

All OAuth variables follow the pattern `OAUTH_<PROVIDER>_<KEY>`:

| Variable | Description |
|---|---|
| `OAUTH_GOOGLE_CLIENT_ID` | Client ID from Google Cloud Console |
| `OAUTH_GOOGLE_CLIENT_SECRET` | Client secret from Google Cloud Console |
| `OAUTH_GOOGLE_REDIRECT_URI` | Redirect URI registered with Google |
| `OAUTH_GITHUB_CLIENT_ID` | Client ID from GitHub OAuth App |
| `OAUTH_GITHUB_CLIENT_SECRET` | Client secret from GitHub OAuth App |
| `OAUTH_GITHUB_REDIRECT_URI` | Redirect URI registered with GitHub |

---

## Google OAuth Registration

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project (or select an existing one).
3. Navigate to **APIs & Services → Credentials**.
4. Click **Create Credentials → OAuth client ID**.
5. Select **Web application** as the application type.
6. Under **Authorized redirect URIs**, add your redirect URI
   (e.g. `http://localhost:8000/auth/google/callback` for local dev).
7. Copy the generated **Client ID** and **Client secret** into `.env`.

---

## GitHub OAuth Registration

1. Go to [GitHub Developer Settings](https://github.com/settings/developers).
2. Click **New OAuth App**.
3. Fill in:
   - **Application name**: your app name
   - **Homepage URL**: your app's base URL
   - **Authorization callback URL**: your redirect URI
     (e.g. `http://localhost:8000/auth/github/callback` for local dev)
4. Click **Register application**.
5. Copy the **Client ID** and generate a **Client secret**, then add both to `.env`.

---

## Loading Configuration in Code

Use `load_oauth_config()` from `oauth_config.py` at application startup:

```python
from oauth_config import load_oauth_config, OAuthConfigError

try:
    # Load whichever providers are configured
    oauth = load_oauth_config()

    # Or require specific providers:
    # oauth = load_oauth_config(require_providers=["google", "github"])
except OAuthConfigError as e:
    print(f"OAuth configuration error: {e}")
    raise SystemExit(1)

google = oauth.get("google")
if google:
    print(f"Google OAuth ready (redirect: {google.redirect_uri})")
```

The module raises `OAuthConfigError` on startup if a provider's configuration
is incomplete (some but not all variables set), making misconfiguration
immediately visible rather than failing at request time.
