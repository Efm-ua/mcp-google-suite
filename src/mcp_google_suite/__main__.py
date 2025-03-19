"""MCP Google Workspace Server entry point."""

import asyncio
import argparse
import os
from pathlib import Path
import mcp.server.stdio
from .server import GoogleWorkspaceMCPServer
from .config import Config
from .auth.google_auth import GoogleAuth
import logging
import sys

logger = logging.getLogger(__name__)

def authenticate(args):
    """Run the authentication flow."""
    config = Config.load(args.config)
    auth = GoogleAuth(config)
    auth.authenticate()

async def run_server():
    """Run the MCP server using stdio transport."""
    try:
        server = GoogleWorkspaceMCPServer()
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MCP Google Workspace Server")
    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Auth command
    auth_parser = subparsers.add_parser(
        "auth", 
        help="Run the authentication flow and save credentials"
    )

    # Run command (default)
    run_parser = subparsers.add_parser(
        "run", 
        help="Run the MCP server"
    )

    args = parser.parse_args()

    if args.command == "auth":
        authenticate(args)
    elif args.command == "run" or args.command is None:
        asyncio.run(run_server())
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 