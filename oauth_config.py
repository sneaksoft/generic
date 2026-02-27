"""OAuth provider configuration module.

Loads and validates OAuth provider credentials from environment variables at startup.
Supports Google and GitHub OAuth providers.

Required environment variables per provider:
  Google:
    OAUTH_GOOGLE_CLIENT_ID      - Google OAuth client ID
    OAUTH_GOOGLE_CLIENT_SECRET  - Google OAuth client secret
    OAUTH_GOOGLE_REDIRECT_URI   - Redirect URI registered with Google

  GitHub:
    OAUTH_GITHUB_CLIENT_ID      - GitHub OAuth app client ID
    OAUTH_GITHUB_CLIENT_SECRET  - GitHub OAuth app client secret
    OAUTH_GITHUB_REDIRECT_URI   - Redirect URI registered with GitHub

See OAUTH_SETUP.md for registration instructions.
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional


class OAuthConfigError(Exception):
    """Raised when OAuth configuration is missing or invalid."""


@dataclass
class OAuthProviderConfig:
    """Configuration for a single OAuth provider."""
    client_id: str
    client_secret: str
    redirect_uri: str
    provider: str


def _load_provider(provider: str, env_prefix: str) -> Optional[OAuthProviderConfig]:
    """Load config for one provider from environment variables.

    Returns None if no variables are set (provider not configured).
    Raises OAuthConfigError if only some variables are set (partial config).
    """
    client_id = os.environ.get(f"{env_prefix}_CLIENT_ID", "")
    client_secret = os.environ.get(f"{env_prefix}_CLIENT_SECRET", "")
    redirect_uri = os.environ.get(f"{env_prefix}_REDIRECT_URI", "")

    values = {"CLIENT_ID": client_id, "CLIENT_SECRET": client_secret, "REDIRECT_URI": redirect_uri}
    set_vars = [k for k, v in values.items() if v]
    missing_vars = [k for k, v in values.items() if not v]

    if not set_vars:
        return None  # Provider not configured

    if missing_vars:
        missing = [f"{env_prefix}_{k}" for k in missing_vars]
        raise OAuthConfigError(
            f"Incomplete {provider} OAuth configuration. Missing: {', '.join(missing)}"
        )

    return OAuthProviderConfig(
        provider=provider,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
    )


# Registry of supported providers: name -> env variable prefix
PROVIDER_ENV_PREFIXES: Dict[str, str] = {
    "google": "OAUTH_GOOGLE",
    "github": "OAUTH_GITHUB",
}


def load_oauth_config(require_providers: Optional[list] = None) -> Dict[str, OAuthProviderConfig]:
    """Load and validate OAuth provider configurations from environment variables.

    Args:
        require_providers: Optional list of provider names that must be configured
                           (e.g. ["google", "github"]). If None, any configured
                           providers are loaded without requiring specific ones.

    Returns:
        Dict mapping provider name to OAuthProviderConfig for each configured provider.

    Raises:
        OAuthConfigError: If a provider has incomplete config, or if a required
                          provider is not configured.
    """
    configs: Dict[str, OAuthProviderConfig] = {}

    for provider, env_prefix in PROVIDER_ENV_PREFIXES.items():
        config = _load_provider(provider, env_prefix)
        if config is not None:
            configs[provider] = config

    if require_providers:
        missing = [p for p in require_providers if p not in configs]
        if missing:
            raise OAuthConfigError(
                f"Required OAuth provider(s) not configured: {', '.join(missing)}. "
                "Set the corresponding environment variables and restart."
            )

    return configs
