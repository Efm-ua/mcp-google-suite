"""Configuration management for MCP Google Workspace."""

import os
from pathlib import Path
from typing import Optional
import json
from pydantic import BaseModel, Field


DEFAULT_ROOT_DIR = os.path.dirname(os.path.join(os.getcwd(),"mcp-google-suite"))
DEFAULT_KEYS_FILE = "gcp-oauth.keys.json"
DEFAULT_CREDENTIALS_FILE = f"{DEFAULT_ROOT_DIR}/.gdrive-server-credentials.json"

class OAuthConfig(BaseModel):
    """OAuth configuration settings."""
    keys_file: str = Field(
        default=DEFAULT_KEYS_FILE,
        description="Path to the OAuth keys JSON file from Google Cloud Console"
    )
    credentials_file: str = Field(
        default=DEFAULT_CREDENTIALS_FILE,
        description="Path to save/load OAuth credentials"
    )

class Config(BaseModel):
    """Main configuration settings."""
    oauth: OAuthConfig = Field(default_factory=OAuthConfig)

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """Load configuration from JSON file."""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                return cls(**file_config)
        return cls()

    def save(self, config_path: str) -> None:
        """Save configuration to JSON file."""
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(self.model_dump(), f, indent=2) 