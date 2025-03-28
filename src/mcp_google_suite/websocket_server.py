import logging

import uvicorn
from mcp.server.websocket import WebsocketServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute

from mcp_google_suite.config import Config
from mcp_google_suite.server import GoogleWorkspaceMCPServer


logger = logging.getLogger(__name__)


class WebSocketGoogleWorkspaceMCPServer(GoogleWorkspaceMCPServer):
    """WebSocket implementation of the Google Workspace MCP server using native SDK transport."""

    def __init__(self, config: Config = None, config_path: str = None):
        super().__init__(config, config_path)
        self.ws = WebsocketServerTransport()
        self.app = Starlette(routes=self._setup_routes())

    def _setup_routes(self):
        """Setup Starlette routes for WebSocket and HTTP endpoints."""
        return [
            Route("/", endpoint=self.root_handler),
            Route("/tools", endpoint=self.tools_handler),
            WebSocketRoute("/ws", endpoint=self.handle_websocket),
        ]

    async def root_handler(self, request):
        """Root endpoint handler."""
        return {"message": "MCP Google Workspace WebSocket Server"}

    async def tools_handler(self, request):
        """Tools endpoint handler."""
        return self._get_tools_list()

    async def handle_websocket(self, websocket):
        """Handle WebSocket connections."""
        async with self.ws.connect_websocket(websocket) as streams:
            await self.server.run(
                streams[0], streams[1], self.server.create_initialization_options()
            )

    def run_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the WebSocket server using uvicorn."""
        uvicorn.run(self.app, host=host, port=port)


if __name__ == "__main__":
    server = WebSocketGoogleWorkspaceMCPServer()
    server.run_server()
