"""Tests for the config module."""

import json
import os
import tempfile
from pathlib import Path

from mcp_google_suite.config import Config, CredentialsConfig


def test_default_config():
    """Test default configuration values."""
    config = Config()
    assert isinstance(config.credentials, CredentialsConfig)
    assert config.credentials.server_credentials.endswith("server-creds.json")
    assert config.credentials.oauth_credentials.endswith("oauth.keys.json")


def test_custom_config():
    """Test loading custom configuration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config.json"
        custom_config = {
            "credentials": {
                "server_credentials": "/custom/path/server-creds.json",
                "oauth_credentials": "/custom/path/oauth.keys.json",
            }
        }
        with open(config_path, "w") as f:
            json.dump(custom_config, f)

        config = Config.load(str(config_path))
        assert config.credentials.server_credentials == "/custom/path/server-creds.json"
        assert config.credentials.oauth_credentials == "/custom/path/oauth.keys.json"


def test_ensure_credentials_dir():
    """Test directory creation for credentials."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_google_dir = Path(temp_dir) / ".google"
        config = Config(
            credentials=CredentialsConfig(
                server_credentials=str(test_google_dir / "server-creds.json"),
                oauth_credentials=str(test_google_dir / "oauth.keys.json"),
            )
        )

        config.ensure_credentials_dir()
        assert test_google_dir.exists()


def test_expanded_paths():
    """Test path expansion in credential paths."""
    config = Config(
        credentials=CredentialsConfig(
            server_credentials="~/test/server-creds.json",
            oauth_credentials="~/test/oauth.keys.json",
        )
    )

    assert config.credentials.expanded_server_credentials == os.path.expanduser(
        "~/test/server-creds.json"
    )
    assert config.credentials.expanded_oauth_credentials == os.path.expanduser(
        "~/test/oauth.keys.json"
    )
