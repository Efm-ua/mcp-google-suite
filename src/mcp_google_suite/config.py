"""Configuration management for MCP Google Workspace."""

import json
import os
from typing import Optional

from pydantic import BaseModel, Field


# Default paths
DEFAULT_GOOGLE_DIR = os.path.expanduser("~/.google")
DEFAULT_SERVER_CREDS = os.path.join(DEFAULT_GOOGLE_DIR, "server-creds.json")
DEFAULT_OAUTH_CREDS = os.path.join(DEFAULT_GOOGLE_DIR, "oauth.keys.json")


class CredentialsConfig(BaseModel):
    """Credentials configuration settings."""

    server_credentials: str = Field(
        default=DEFAULT_SERVER_CREDS, description="Path to the server credentials JSON file"
    )
    oauth_credentials: str = Field(
        default=DEFAULT_OAUTH_CREDS, description="Path to the OAuth credentials JSON file"
    )

    def ensure_credentials_dir(self) -> None:
        """Ensure the credentials directory exists."""
        for cred_path in [self.server_credentials, self.oauth_credentials]:
            os.makedirs(os.path.dirname(os.path.expanduser(cred_path)), exist_ok=True)

    @property
    def expanded_server_credentials(self) -> str:
        """Get the expanded path for server credentials."""
        return os.path.expanduser(self.server_credentials)

    @property
    def expanded_oauth_credentials(self) -> str:
        """Get the expanded path for OAuth credentials."""
        return os.path.expanduser(self.oauth_credentials)


class Config(BaseModel):
    """Main configuration settings."""

    credentials: CredentialsConfig = Field(default_factory=CredentialsConfig)

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """Load configuration from JSON file."""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                file_config = json.load(f)
                return cls(**file_config)
        return cls()

    def save(self, config_path: str) -> None:
        """Save configuration to JSON file."""
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(self.model_dump(), f, indent=2)

    def ensure_credentials_dir(self) -> None:
        """Ensure the credentials directory exists."""
        self.credentials.ensure_credentials_dir()
