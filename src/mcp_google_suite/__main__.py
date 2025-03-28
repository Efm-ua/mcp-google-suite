"""Main entry point for the MCP Google Suite server."""

import asyncio
import logging
import sys
from typing import Optional

from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions, ServerCapabilities
from mcp.server import NotificationOptions
from mcp_google_suite.server import GoogleWorkspaceMCPServer


def main() -> Optional[int]:
    """Run the MCP Google Suite server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    try:
        # Create server instance
        server = GoogleWorkspaceMCPServer()

        # Create initialization options
        init_options = InitializationOptions(
            server_name="mcp-google-suite",
            server_version="0.1.0",
            capabilities=server.server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            ),
        )

        async def run_server():
            try:
                async with stdio_server() as (read_stream, write_stream):
                    await server.run(read_stream, write_stream, init_options)
            except KeyboardInterrupt:
                logger.info("Server stopped by user")
            except Exception as e:
                logger.error(f"Server error: {e}", exc_info=True)
                raise

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