"""Google OAuth authentication module."""

from typing import Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import json
import asyncio
from mcp_google_suite.config import Config, OAuthConfig, DEFAULT_KEYS_FILE, DEFAULT_CREDENTIALS_FILE

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets'
]

class GoogleAuth:
    """Handles Google OAuth2 authentication."""
    
    def __init__(self, config: Optional[Config] = None, config_path: Optional[str] = None):
        """Initialize authentication with optional config or config_path."""
        self.config = config or Config.load(config_path)
        self.creds: Optional[Credentials] = None
        self._creds_lock = asyncio.Lock()

    async def authenticate(self) -> None:
        """Run the authentication flow and save credentials."""
        if not os.path.exists(self.config.oauth.keys_file):
            raise FileNotFoundError(
                f"OAuth keys file not found at {self.config.oauth.keys_file}. "
                "Please follow these steps:\n"
                "1. Create a new Google Cloud project\n"
                "2. Enable the Google Drive, Docs, and Sheets APIs\n"
                "3. Configure OAuth consent screen\n"
                "4. Create OAuth Client ID for Desktop App\n"
                "5. Download the JSON file and save as 'gcp-oauth.keys.json'\n"
                "   in the root directory"
            )
        print(f"Authenticating Saving to  {self.config.oauth.credentials_file}")
        
        # Run the flow in a thread since it's blocking
        flow = await asyncio.to_thread(
            InstalledAppFlow.from_client_secrets_file,
            self.config.oauth.keys_file, 
            SCOPES
        )
        self.creds = await asyncio.to_thread(flow.run_local_server, port=0)

        # Save the credentials
        await asyncio.to_thread(os.makedirs, os.path.dirname(self.config.oauth.credentials_file), exist_ok=True)
        await asyncio.to_thread(self._save_credentials)

        print(f"\nAuthentication successful!")
        print(f"Credentials saved to: {self.config.oauth.credentials_file}")

    def _save_credentials(self) -> None:
        """Save credentials to file (helper method for async operations)."""
        if self.creds:
            with open(self.config.oauth.credentials_file, 'w') as f:
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
            if os.path.exists(self.config.oauth.credentials_file):
                self.creds = await asyncio.to_thread(
                    Credentials.from_authorized_user_file,
                    self.config.oauth.credentials_file, 
                    SCOPES
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