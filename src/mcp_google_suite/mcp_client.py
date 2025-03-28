import asyncio
import logging
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S,%03d",
)
logger = logging.getLogger(__name__)

# Get the workspace directory
WORKSPACE_DIR = "/Users/ashok/projects/adex/mcp-servers/mcp-google-suite"


async def main() -> None:
    """Main entry point for the client."""
    logger.info("Starting client...")

    # Setup server parameters
    params = StdioServerParameters(
        command="uv", args=["--directory", WORKSPACE_DIR, "run", "mcp-google"]
    )

    # Create client session
    async with stdio_client(params) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            # Initialize session
            await session.initialize()
            logger.info("Session initialized successfully")

            # List available tools
            tools = await session.list_tools()
            logger.info(f"Available tools: {tools}")

            # Create a test document
            logger.info("Creating test document...")
            result = await session.call_tool(
                "docs_create", {"title": "Test Document", "content": "Hello from MCP client!"}
            )
            logger.info(f"Document creation result: {result}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Client stopped by user")
    except Exception as e:
        logger.error(f"Client error: {e}", exc_info=True)
        sys.exit(1)
