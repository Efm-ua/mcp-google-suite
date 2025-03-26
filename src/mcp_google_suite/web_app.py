"""Web application module for MCP Google Workspace Server."""

from mcp.server.sse import SseServerTransport
from mcp.server.websocket import websocket_server
from starlette.applications import Starlette
from starlette.routing import Mount, Route, WebSocketRoute

from mcp_google_suite.server import GoogleWorkspaceMCPServer


def create_web_app(server: GoogleWorkspaceMCPServer) -> Starlette:
    """Create a Starlette application with both SSE and WebSocket support."""

    # Initialize SSE transport
    sse = SseServerTransport("/messages/")

    async def root(request):
        return {"message": "MCP Google Workspace Server"}

    async def tools(request):
        return server._get_tools_list()

    async def handle_sse(request):
        """Handle SSE connections."""
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(streams[0], streams[1])

    async def handle_websocket(websocket):
        """Handle WebSocket connections."""
        async with websocket_server(websocket.scope, websocket.receive, websocket.send) as streams:
            await server.run(streams[0], streams[1])

    # Define routes for both SSE and WebSocket
    routes = [
        Route("/", endpoint=root),
        Route("/tools", endpoint=tools),
        Route("/sse", endpoint=handle_sse),
        Mount("/messages", app=sse.handle_post_message),
        WebSocketRoute("/ws", endpoint=handle_websocket),
    ]

    return Starlette(routes=routes)
