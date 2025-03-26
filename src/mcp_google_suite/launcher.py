#!/usr/bin/env python3
"""MCP Google Workspace Server launcher with environment and argument support.

This module provides the main entry point for the MCP Google Workspace server.
The server can be run in different modes (stdio, sse, ws) and supports both
direct execution and inspection via the MCP Inspector tool.

Usage:
    Direct execution:
        mcp-google                    # Run server in stdio mode
        mcp-google run               # Same as above
        mcp-google run --mode ws     # Run in WebSocket mode
        mcp-google auth              # Run authentication flow

    With MCP Inspector:
        npx @modelcontextprotocol/inspector uv run mcp-google

    Environment Variables:
        SERVER_MODE: stdio|sse|ws    # Override server transport mode
        HOST: str                    # Host for HTTP/WebSocket server
        PORT: int                    # Port for HTTP/WebSocket server

Note:
    When using the MCP Inspector, the server automatically uses stdio mode
    for communication with the inspector tool. The inspector provides a UI
    for testing and debugging MCP server functionality.
"""

import argparse
import asyncio
import os
from typing import Dict, List

import mcp.server.stdio
import uvicorn
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions

from mcp_google_suite.auth.google_auth import GoogleAuth
from mcp_google_suite.config import Config
from mcp_google_suite.server import GoogleWorkspaceMCPServer
from mcp_google_suite.web_app import create_web_app


def parse_env_vars(env_vars: List[str]) -> Dict[str, str]:
    """Parse environment variables from KEY=value format."""
    result = {}
    for env_var in env_vars:
        try:
            key, value = env_var.split("=", 1)
            # Handle shell variable expansion
            result[key] = os.path.expandvars(value)
        except ValueError:
            print(f"Warning: Skipping invalid environment variable format: {env_var}")
    return result


def create_init_options(server: GoogleWorkspaceMCPServer) -> InitializationOptions:
    """Create initialization options for the server."""
    return InitializationOptions(
        server_name="mcp-google-suite",
        server_version="0.1.0",
        capabilities=server.server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )


async def run_stdio_server(server: GoogleWorkspaceMCPServer):
    """Run the server in stdio mode."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            create_init_options(server),
        )


def authenticate(config_path: str = None):
    """Run the authentication flow."""
    config = Config.load(config_path)
    auth = GoogleAuth(config)
    auth.authenticate()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MCP Google Workspace Server")
    parser.add_argument(
        "command",
        nargs="?",  # Make command optional
        choices=["run", "auth"],
        default="run",  # Default to "run" if not provided
        help="Command to execute (run: start server, auth: authenticate)",
    )
    parser.add_argument(
        "--mode",
        choices=["stdio", "sse", "ws"],
        default="stdio",
        help="Server transport mode (default: stdio)",
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host for HTTP/WebSocket server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port for HTTP/WebSocket server (default: 8000)"
    )
    parser.add_argument("--config", help="Path to configuration file")

    args = parser.parse_args()

    if args.command == "auth":
        authenticate(args.config)
        return

    # Create server instance with config if provided
    server = GoogleWorkspaceMCPServer(config_path=args.config)

    # Override mode from environment if not specified in args
    mode = args.mode or os.environ.get("SERVER_MODE", "stdio")

    if mode == "stdio":
        # Run in STDIO mode using MCP's transport
        asyncio.run(run_stdio_server(server))
    else:
        # Create web app for SSE/WS modes
        app = create_web_app(server)
        host = args.host or os.environ.get("HOST", "0.0.0.0")
        port = args.port or int(os.environ.get("PORT", "8000"))
        uvicorn.run(app, host=host, port=port)


def run_server():
    """Backward compatibility wrapper around main()."""
    import sys

    # If no arguments provided, default to 'run'
    if len(sys.argv) == 1:
        sys.argv.append("run")
    main()


if __name__ == "__main__":
    main()
