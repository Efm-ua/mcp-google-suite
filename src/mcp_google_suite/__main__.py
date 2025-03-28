"""Main entry point for the MCP Google Suite server."""

import asyncio
import logging
import sys

from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import ResourcesCapability, ServerCapabilities, ToolsCapability

from mcp_google_suite.server import GoogleWorkspaceMCPServer


def main() -> int:
    """Run the MCP Google Suite server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    try:
        # Create server instance
        server = GoogleWorkspaceMCPServer()

        async def run_server():
            try:
                # Use the MCP SDK's stdio_server context manager
                async with stdio_server() as (read_stream, write_stream):
                    # Run server with initialization options
                    init_options = InitializationOptions(
                        server_name="mcp-google-suite",
                        server_version="0.1.0",
                        capabilities=ServerCapabilities(
                            tools=ToolsCapability(enabled=True),
                            resources=ResourcesCapability(enabled=False),
                            experimental={
                                "tools": {"enabled": True},
                                "resources": {"enabled": False},
                                "streaming": {"enabled": False},
                            },
                        ),
                    )
                    await server.run(read_stream, write_stream, init_options)
            except Exception as e:
                if "client closed" in str(e).lower():
                    logger.info("Client disconnected")
                    return
                logger.error(f"Server error: {e}", exc_info=True)
                raise

        # Run the server
        asyncio.run(run_server())
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
