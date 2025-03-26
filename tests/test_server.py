"""Integration test for MCP server."""

import pytest

from mcp_google_suite.config import Config
from mcp_google_suite.server import GoogleWorkspaceMCPServer


@pytest.mark.asyncio
async def test_server_tools():
    """Test that server can start and list tools."""
    config = Config()
    server = GoogleWorkspaceMCPServer(config)

    # Get the list of tools
    tools = server._get_tools_list()

    # Verify essential tools are present
    tool_names = {tool.name for tool in tools}
    expected_tools = {
        "drive_search_files",
        "drive_create_folder",
        "docs_create",
        "docs_get_content",
        "docs_update_content",
        "sheets_create",
        "sheets_get_values",
        "sheets_update_values",
    }

    assert expected_tools.issubset(tool_names), "Not all expected tools are available"
