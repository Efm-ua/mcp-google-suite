"""Google OAuth authentication module."""

import asyncio
import os
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from mcp_google_suite.config import Config


SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
]


class GoogleAuth:
    """Handles Google OAuth2 authentication."""

    def __init__(self, config: Optional[Config] = None, config_path: Optional[str] = None):
        """Initialize authentication with optional config or config_path."""
        self.config = config or Config.load(config_path)
        self.creds: Optional[Credentials] = None
        self._creds_lock = asyncio.Lock()
        # Ensure credentials directory exists
        self.config.ensure_credentials_dir()

    async def authenticate(self) -> None:
        """Run the authentication flow and save credentials."""
        oauth_creds_path = self.config.credentials.expanded_oauth_credentials
        server_creds_path = self.config.credentials.expanded_server_credentials

        if not os.path.exists(oauth_creds_path):
            raise FileNotFoundError(
                f"OAuth keys file not found at {oauth_creds_path}. "
                "Please follow these steps:\n"
                "1. Create a new Google Cloud project\n"
                "2. Enable the Google Drive, Docs, and Sheets APIs\n"
                "3. Configure OAuth consent screen\n"
                "4. Create OAuth Client ID for Desktop App\n"
                "5. Download the JSON file and save as 'oauth.keys.json'\n"
                "   in the ~/.google directory"
            )
        print(f"Authenticating and saving credentials to {server_creds_path}")

        # Run the flow in a thread since it's blocking
        flow = await asyncio.to_thread(
            InstalledAppFlow.from_client_secrets_file, oauth_creds_path, SCOPES
        )
        self.creds = await asyncio.to_thread(flow.run_local_server, port=0)

        # Save the credentials
        await asyncio.to_thread(self._save_credentials)

        print("\nAuthentication successful!")
        print(f"Credentials saved to: {server_creds_path}")

    def _save_credentials(self) -> None:
        """Save credentials to file (helper method for async operations)."""
        if self.creds:
            with open(self.config.credentials.expanded_server_credentials, "w") as f:
                f.write(self.creds.to_json())

    async def get_credentials(self) -> Credentials:
        """Get and refresh Google OAuth2 credentials asynchronously."""
        async with self._creds_lock:
            if self.creds and self.creds.valid:
                return self.creds

            if self.creds and self.creds.expired and self.creds.refresh_token:
                await asyncio.to_thread(self.creds.refresh, Request())
                await asyncio.to_thread(self._save_credentials)
                return self.creds

            # Try to load saved credentials
            server_creds_path = self.config.credentials.expanded_server_credentials
            if os.path.exists(server_creds_path):
                self.creds = await asyncio.to_thread(
                    Credentials.from_authorized_user_file, server_creds_path, SCOPES
                )

                if self.creds.valid:
                    return self.creds

                if self.creds.expired and self.creds.refresh_token:
                    await asyncio.to_thread(self.creds.refresh, Request())
                    await asyncio.to_thread(self._save_credentials)
                    return self.creds

            raise FileNotFoundError(
                "No valid credentials found. "
                "Please run authentication first: python -m mcp_google_suite auth"
            )

    async def is_authorized(self) -> bool:
        """Check if we have valid credentials asynchronously."""
        try:
            await self.get_credentials()
            return True
        except FileNotFoundError:
            return False

    @property
    def authorized(self) -> bool:
        """Synchronous check for valid credentials (use is_authorized for async code)."""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.is_authorized())
        except FileNotFoundError:
            return False
