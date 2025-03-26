import asyncio
from typing import Any, Dict, Optional

from googleapiclient.discovery import build

from mcp_google_suite.auth.google_auth import GoogleAuth


class BaseGoogleService:
    """Base class for Google Workspace services."""

    def __init__(self, service_name: str, version: str, auth: Optional[GoogleAuth] = None):
        self.service_name = service_name
        self.version = version
        self.auth = auth or GoogleAuth()
        self._service = None
        self._service_lock = asyncio.Lock()

    async def get_service(self) -> Any:
        """Get the Google service client asynchronously."""
        if not self._service:
            async with self._service_lock:
                if not self._service:  # Double check pattern
                    credentials = await self.auth.get_credentials()
                    self._service = build(self.service_name, self.version, credentials=credentials)
        return self._service

    @property
    def service(self) -> Any:
        """
        Synchronous access to service - should only be used within async methods
        after get_service() has been called.
        """
        if not self._service:
            raise RuntimeError("Service not initialized. Call get_service() first")
        return self._service

    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle and format service errors."""
        error_details = {"error": str(error), "type": error.__class__.__name__}

        if hasattr(error, "resp") and hasattr(error.resp, "status"):
            error_details["status"] = error.resp.status

        return error_details
