import logging

import uvicorn
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route

from mcp_google_suite.config import Config
from mcp_google_suite.server import GoogleWorkspaceMCPServer


logger = logging.getLogger(__name__)


class SSEGoogleWorkspaceMCPServer(GoogleWorkspaceMCPServer):
    """SSE implementation of the Google Workspace MCP server using native SDK transport."""

    def __init__(self, config: Config = None, config_path: str = None):
        super().__init__(config, config_path)
        self.sse = SseServerTransport("/messages/")
        self.app = Starlette(routes=self._setup_routes())

    def _setup_routes(self):
        """Setup Starlette routes for SSE and message handling."""
        return [
            Route("/", endpoint=self.root_handler),
            Route("/tools", endpoint=self.tools_handler),
            Route("/sse", endpoint=self.handle_sse),
            Mount("/messages", app=self.sse.handle_post_message),
        ]

    async def root_handler(self, request):
        """Root endpoint handler."""
        return {"message": "MCP Google Workspace SSE Server"}

    async def tools_handler(self, request):
        """Tools endpoint handler."""
        return self._get_tools_list()

    async def handle_sse(self, request):
        """Handle SSE connections."""
        async with self.sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await self.server.run(
                streams[0], streams[1], self.server.create_initialization_options()
            )

    def run_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the SSE server using uvicorn."""
        uvicorn.run(self.app, host=host, port=port)


if __name__ == "__main__":
    server = SSEGoogleWorkspaceMCPServer()
    server.run_server()
