"""
Модуль: web_app
Призначення: HTTP-адаптер для MCP Google Workspace Server
Залежності: mcp.server, starlette, GoogleWorkspaceMCPServer
Експортує: create_web_app функцію для створення Starlette додатку з HTTP ендпоінтами
"""

import json
import logging
from mcp.server.sse import SseServerTransport
from mcp.server.websocket import websocket_server
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route, WebSocketRoute

from mcp_google_suite.server import GoogleWorkspaceMCPServer, GoogleWorkspaceContext
from mcp_google_suite.auth.google_auth import GoogleAuth
from mcp_google_suite.docs.service import DocsService
from mcp_google_suite.drive.service import DriveService
from mcp_google_suite.sheets.service import SheetsService

# Configure logging
logger = logging.getLogger(__name__)


def create_web_app(server: GoogleWorkspaceMCPServer) -> Starlette:
    """Create a Starlette application with both SSE and WebSocket support."""

    # Initialize SSE transport
    sse = SseServerTransport("/messages/")

    async def root(request):
        return JSONResponse({"message": "MCP Google Workspace Server", "status": "healthy"})

    async def health(request):
        """Health check endpoint returning {"status": "ok"}."""
        return JSONResponse({"status": "ok"})

    async def tools(request):
        try:
            tools_list = server._get_tools_list()
            # Convert Tool objects to dictionaries for JSON serialization
            tools_dict = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools_list
            ]
            return JSONResponse({"tools": tools_dict})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    async def invoke_tool(request: Request):
        """
        HTTP-адаптер для виклику MCP інструментів.
        Приймає POST запити з JSON тілом: {"tool_name": "...", "params": {...}}
        Повертає результат виклику інструменту або помилку.
        """
        try:
            # Parse request body
            body = await request.json()
            tool_name = body.get("tool_name")
            params = body.get("params", {})

            if not tool_name:
                return JSONResponse(
                    {"error": "Missing required field: tool_name"}, 
                    status_code=400
                )

            logger.info(f"HTTP adapter invoking tool: {tool_name} with params: {params}")

            # Handle special system tools
            if tool_name == "system.list_tools":
                tools = server._get_tools_list()
                tool_names = [tool.name for tool in tools]
                return JSONResponse({"tools": tool_names})

            # Check if server context is initialized
            if not server._context:
                # Initialize context for HTTP requests (permanently)
                auth = GoogleAuth(config=server.config)
                drive = DriveService(auth)
                docs = DocsService(auth)
                sheets = SheetsService(auth)
                server._context = GoogleWorkspaceContext(
                    auth=auth, drive=drive, docs=docs, sheets=sheets
                )
                logger.info("HTTP adapter: Initialized server context for web requests")

            return await _execute_tool(server, tool_name, params)

        except json.JSONDecodeError:
            return JSONResponse(
                {"error": "Invalid JSON in request body"}, 
                status_code=400
            )
        except Exception as e:
            logger.error(f"Error invoking tool {tool_name}: {str(e)}", exc_info=True)
            return JSONResponse(
                {"error": f"Tool execution failed: {str(e)}"}, 
                status_code=500
            )

    async def _execute_tool(server: GoogleWorkspaceMCPServer, tool_name: str, params: dict):
        """Execute a tool using the server's internal logic."""
        try:
            # Check if tool exists
            handler = server._tool_registry.get(tool_name)
            if not handler:
                available_tools = list(server._tool_registry.keys())
                return JSONResponse(
                    {
                        "error": f"Unknown tool: {tool_name}",
                        "available_tools": available_tools
                    }, 
                    status_code=404
                )

            # Check authentication
            is_authorized = await server._context.auth.is_authorized()
            if not is_authorized:
                return JSONResponse(
                    {"error": "Not authenticated. Please run 'mcp-google auth' first."}, 
                    status_code=401
                )

            # Execute the tool
            result = await handler(server._context, params)
            
            logger.info(f"Tool {tool_name} executed successfully")
            return JSONResponse({"result": result})

        except ValueError as e:
            return JSONResponse(
                {"error": f"Invalid parameters: {str(e)}"}, 
                status_code=400
            )
        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}", exc_info=True)
            return JSONResponse(
                {"error": f"Tool execution failed: {str(e)}"}, 
                status_code=500
            )

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
        Route("/health", endpoint=health),
        Route("/tools", endpoint=tools),
        Route("/invoke-tool", endpoint=invoke_tool, methods=["POST"]),
        Route("/sse", endpoint=handle_sse),
        Mount("/messages", app=sse.handle_post_message),
        WebSocketRoute("/ws", endpoint=handle_websocket),
    ]

    return Starlette(routes=routes)
